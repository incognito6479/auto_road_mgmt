"""
management/serializers.py

DRF serializers for all management models.
"""

from django.db import transaction
from rest_framework import serializers
from django.db.models import Sum

from management.models import Category, Student, User, Enrollment, Payment, Group, LearningPlace


# ---------------------------------------------------------------------------
# Category
# ---------------------------------------------------------------------------

class CategorySerializer(serializers.ModelSerializer):
    registered = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "name", "price", "duration", "is_active", "registered", "notes", "created_at", "updated_at"]
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

    jshshr = serializers.IntegerField(required=False, allow_null=True)
    passport_serie = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    passport_number = serializers.IntegerField(required=False, allow_null=True)

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
            "is_superuser",
            "date_joined",
        ]
        read_only_fields = ["id", "date_joined"]
        extra_kwargs = {
            "password": {"write_only": True, "required": False},
            "jshshr": {"required": False, "allow_null": True},
            "passport_serie": {"required": False, "allow_blank": True, "allow_null": True},
            "passport_number": {"required": False, "allow_null": True},
        }

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
            "phone2",
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
            "phone2",
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


class LearningPlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningPlace
        fields = ["id", "place_name", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class EnrollmentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.full_name", read_only=True)
    student_phone = serializers.CharField(source="student.phone", read_only=True)
    student_phone2 = serializers.CharField(source="student.phone2", read_only=True)
    student_jshshr = serializers.CharField(source="student.jshshr", read_only=True)
    instructor_name = serializers.SerializerMethodField()
    coordinator_name = serializers.SerializerMethodField()
    learning_place_name = serializers.CharField(source="learning_place.place_name", read_only=True)
    paid_amount = serializers.SerializerMethodField()

    class Meta:
        model = Enrollment
        fields = [
            "id", "student", "student_name", "student_phone", "student_phone2", "student_jshshr",
            "category", "group", "instructor", "instructor_name", "coordinator", "coordinator_name",
            "learning_place", "learning_place_name", "learning_time", "learning_days", "status",
            "enrolled_free", "enrolled_amount", "paid_amount", "notes",
            "is_active", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_instructor_name(self, obj):
        if obj.instructor:
            name = f"{obj.instructor.first_name} {obj.instructor.last_name}".strip()
            return name or obj.instructor.phone
        return None

    def get_coordinator_name(self, obj):
        if obj.coordinator:
            name = f"{obj.coordinator.first_name} {obj.coordinator.last_name}".strip()
            return name or obj.coordinator.phone
        return None

    def get_paid_amount(self, obj):
        result = obj.payments.filter(status="accepted", is_active=True).aggregate(total=Sum("amount"))
        return result["total"] or 0


class PaymentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="enrollment.student.full_name", read_only=True)
    student_jshshr = serializers.CharField(source="enrollment.student.jshshr", read_only=True)
    category_name = serializers.CharField(source="enrollment.category.name", read_only=True)
    cashier_name = serializers.CharField(source="user.phone", read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id", "user", "cashier_name", "enrollment", "student_name", "student_jshshr", "category_name",
            "amount", "status", "method", "notes", "is_active", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class GroupSerializer(serializers.ModelSerializer):
    student_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    student_count = serializers.SerializerMethodField()
    category_name = serializers.CharField(source="category.name", read_only=True)
    enrollments = EnrollmentSerializer(many=True, read_only=True)

    class Meta:
        model = Group
        fields = [
            "id", "category", "category_name", "name", "started_at",
            "duration", "status", "student_ids", "student_count",
            "enrollments", "notes", "is_active", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "created_at", "updated_at", "student_count"]

    def get_student_count(self, obj):
        return obj.enrollments.count()

    def create(self, validated_data):
        student_ids = validated_data.pop("student_ids", [])
        category = validated_data.get("category")
        
        with transaction.atomic():
            group = Group.objects.create(**validated_data)
            if student_ids and category:
                # Find active enrollments of these students in this category
                enrollments = Enrollment.objects.filter(
                    student_id__in=student_ids,
                    category=category,
                    is_active=True
                )
                # Update their group and status to enrolled
                enrollments.update(group=group, status=Enrollment.Status.ENROLLED)
                
        return group
