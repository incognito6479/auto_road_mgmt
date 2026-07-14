"""
management/serializers.py

DRF serializers for all management models.
"""

from django.db import transaction
from rest_framework import serializers

from management.models import Category, Student, User, Enrollment, Payment


# ---------------------------------------------------------------------------
# Category
# ---------------------------------------------------------------------------

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "price", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


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
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_category(self, obj):
        # Retrieve category name from the first active enrollment
        enrollment = obj.enrollments.filter(is_active=True).first()
        return enrollment.category.name if enrollment else None


class StudentCreateSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.filter(is_active=True),
        write_only=True,
    )
    min_payment = serializers.IntegerField(
        write_only=True,
        min_value=0,
    )

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
        ]

    def create(self, validated_data):
        category = validated_data.pop("category")
        min_payment = validated_data.pop("min_payment")
        
        request = self.context.get("request")
        user = request.user if request else None

        with transaction.atomic():
            # Create the student, defaulting status to enrolled as they are paying
            student = Student.objects.create(
                status=Student.Status.ENROLLED,
                **validated_data
            )

            # Create Enrollment
            Enrollment.objects.create(
                student=student,
                category=category,
                status=Enrollment.Status.ENROLLED,
            )

            # Create Payment
            Payment.objects.create(
                user=user,
                student=student,
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
        fields = ["id", "student", "category", "status", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["id", "user", "student", "amount", "status", "method", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
