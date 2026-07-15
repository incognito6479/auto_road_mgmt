"""
management/serializers.py

DRF serializers for all management models.
"""

from django.db import transaction
from rest_framework import serializers
from django.db.models import Sum

from management.models import Category, Student, User, Enrollment, Payment


# ---------------------------------------------------------------------------
# Category
# ---------------------------------------------------------------------------

class CategorySerializer(serializers.ModelSerializer):
    registered = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "name", "price", "is_active", "registered", "notes", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_registered(self, obj):
        return Student.objects.filter(
            enrollments__category=obj,
            enrollments__is_active=True,
            enrollments__status=Enrollment.Status.NEW
        ).count()


# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------

class UserSerializer(serializers.ModelSerializer):
    """
    General-purpose user serializer.
    `password` is write-only: accepted on create/update, never returned.
    """

    password = serializers.CharField(
        write_only=True,
        required=False,
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = [
            "id",
            "phone",
            "role",
            "first_name",
            "last_name",
            "email",
            "jshshr",
            "passport_serie",
            "passport_number",
            "password",
            "is_active",
            "is_staff",
            "date_joined",
        ]
        read_only_fields = ["id", "date_joined"]

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


# ---------------------------------------------------------------------------
# Student
# ---------------------------------------------------------------------------

class StudentSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    category_id = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    payment_amount = serializers.SerializerMethodField()
    enrolled_free = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = [
            "id",
            "full_name",
            "phone",
            "jshshr",
            "passport_serie",
            "passport_number",
            "status",
            "category",
            "category_id",
            "payment_amount",
            "enrolled_free",
            "notes",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_category(self, obj):
        # Retrieve category name from the first active enrollment
        enrollment = obj.enrollments.filter(is_active=True).first()
        return enrollment.category.name if enrollment else None

    def get_category_id(self, obj):
        enrollment = obj.enrollments.filter(is_active=True).first()
        return enrollment.category.id if enrollment else None

    def get_status(self, obj):
        enrollment = obj.enrollments.filter(is_active=True).first()
        return enrollment.status if enrollment else None

    def get_enrolled_free(self, obj):
        enrollment = obj.enrollments.filter(is_active=True).first()
        return enrollment.enrolled_free if enrollment else False

    def get_payment_amount(self, obj):
        enrollment = obj.enrollments.filter(is_active=True).first()
        if not enrollment:
            return 0
        result = enrollment.payments.filter(is_active=True).aggregate(total=Sum("amount"))
        return result["total"] or 0

    def update(self, instance, validated_data):
        request = self.context.get("request")
        category_id = request.data.get("category") if request else None
        status_val = request.data.get("status") if request else None

        with transaction.atomic():
            student = super().update(instance, validated_data)
            enrollment = student.enrollments.filter(is_active=True).first()
            if enrollment:
                if category_id is not None:
                    if category_id:
                        try:
                            category = Category.objects.get(id=category_id, is_active=True)
                            enrollment.category = category
                        except Category.DoesNotExist:
                            pass
                if status_val is not None:
                    enrollment.status = status_val
                enrollment.save()
            else:
                if category_id:
                    try:
                        category = Category.objects.get(id=category_id, is_active=True)
                        Enrollment.objects.create(
                            student=student,
                            category=category,
                            status=status_val or Enrollment.Status.ENROLLED,
                        )
                    except Category.DoesNotExist:
                        pass
        return student


class StudentCreateSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.filter(is_active=True),
        write_only=True,
    )
    min_payment = serializers.IntegerField(
        write_only=True,
        min_value=0,
    )
    status = serializers.ChoiceField(
        choices=Enrollment.Status.choices,
        default=Enrollment.Status.ENROLLED,
        write_only=True,
    )
    enrolled_free = serializers.BooleanField(
        write_only=True,
        default=False,
    )
    enrolled_amount = serializers.IntegerField(
        write_only=True,
        required=False,
        allow_null=True,
    )
    payment_amount = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = [
            "id",
            "full_name",
            "phone",
            "jshshr",
            "passport_serie",
            "passport_number",
            "status",
            "category",
            "min_payment",
            "enrolled_free",
            "enrolled_amount",
            "payment_amount",
            "notes",
        ]
        read_only_fields = ["id", "payment_amount"]

    def get_payment_amount(self, obj):
        enrollment = obj.enrollments.filter(is_active=True).first()
        if not enrollment:
            return 0
        result = enrollment.payments.filter(is_active=True).aggregate(total=Sum("amount"))
        return result["total"] or 0

    def create(self, validated_data):
        category = validated_data.pop("category")
        min_payment = validated_data.pop("min_payment")
        enrollment_status = validated_data.pop("status", Enrollment.Status.ENROLLED)
        enrolled_free = validated_data.pop("enrolled_free", False)
        enrolled_amount = validated_data.pop("enrolled_amount", None)

        if enrolled_free:
            enrolled_amount = 0
        elif enrolled_amount is None:
            enrolled_amount = category.price
        
        request = self.context.get("request")
        user = request.user if request else None

        with transaction.atomic():
            student = Student.objects.create(**validated_data)

            # Create Enrollment
            enrollment = Enrollment.objects.create(
                student=student,
                category=category,
                status=enrollment_status,
                enrolled_free=enrolled_free,
                enrolled_amount=enrolled_amount,
            )

            # Create Payment
            Payment.objects.create(
                user=user,
                enrollment=enrollment,
                amount=min_payment,
                status=Payment.Status.ACCEPTED,
                method=Payment.Method.CASH,
            )

        return student


# ---------------------------------------------------------------------------
# Enrollment & Payment
# ---------------------------------------------------------------------------

class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ["id", "student", "category", "status", "enrolled_free", "enrolled_amount", "notes", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["id", "user", "enrollment", "amount", "status", "method", "notes", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
