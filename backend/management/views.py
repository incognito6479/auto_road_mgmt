"""
management/views.py

All application views for the Driving School Management app live here.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from management.models import Category, Student, User, Enrollment, Payment
from management.serializers import (
    CategorySerializer,
    StudentSerializer,
    UserSerializer,
    StudentCreateSerializer,
    EnrollmentSerializer,
    PaymentSerializer,
)


# ---------------------------------------------------------------------------
# Base viewset: soft-delete (sets is_active=False instead of deleting)
# ---------------------------------------------------------------------------

class SoftDeleteModelViewSet(viewsets.ModelViewSet):
    """
    A ModelViewSet where `destroy` performs a soft-delete:
    sets `is_active = False` on the instance instead of removing it from the DB.
    """

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save(update_fields=["is_active"])
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------------------
# Category
# ---------------------------------------------------------------------------

class CategoryViewSet(SoftDeleteModelViewSet):
    """CRUD for driving licence categories."""

    queryset = Category.objects.filter(is_active=True).order_by("name")
    serializer_class = CategorySerializer


# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------

class UserViewSet(SoftDeleteModelViewSet):
    """CRUD for system users (staff/instructors/etc.)."""

    queryset = User.objects.filter(is_active=True).order_by("phone")
    serializer_class = UserSerializer


# ---------------------------------------------------------------------------
# Student
# ---------------------------------------------------------------------------

class StudentViewSet(SoftDeleteModelViewSet):
    """CRUD for driving school students."""

    queryset = Student.objects.filter(is_active=True).order_by("full_name")
    serializer_class = StudentSerializer

    def get_serializer_class(self):
        if self.action == "create":
            return StudentCreateSerializer
        return StudentSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        category_id = self.request.query_params.get("category")
        status = self.request.query_params.get("status")
        if category_id:
            queryset = queryset.filter(enrollments__category_id=category_id, enrollments__is_active=True)
        if status:
            queryset = queryset.filter(enrollments__status=status, enrollments__is_active=True)
        return queryset


# ---------------------------------------------------------------------------
# Enrollment
# ---------------------------------------------------------------------------

class EnrollmentViewSet(SoftDeleteModelViewSet):
    """CRUD for student enrollments."""

    queryset = Enrollment.objects.filter(is_active=True).order_by("-created_at")
    serializer_class = EnrollmentSerializer


# ---------------------------------------------------------------------------
# Payment
# ---------------------------------------------------------------------------

class PaymentViewSet(SoftDeleteModelViewSet):
    """CRUD for student payments."""

    queryset = Payment.objects.filter(is_active=True).order_by("-created_at")
    serializer_class = PaymentSerializer
