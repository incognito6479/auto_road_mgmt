"""
management/views.py

All application views for the Driving School Management app live here.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from management.models import Category, Student, User, Enrollment, Payment, Group, LearningPlace
from management.serializers import (
    CategorySerializer,
    StudentSerializer,
    UserSerializer,
    StudentCreateSerializer,
    EnrollmentSerializer,
    PaymentSerializer,
    GroupSerializer,
    LearningPlaceSerializer,
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
# Custom standard pagination
# ---------------------------------------------------------------------------

class StandardPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = "page_size"
    max_page_size = 100


def is_admin_or_superuser(user):
    if not user or not user.is_authenticated:
        return False
    return user.is_superuser or user.role in [User.Role.ADMIN, User.Role.SUPERUSER]


# ---------------------------------------------------------------------------
# Category
# ---------------------------------------------------------------------------

class CategoryViewSet(SoftDeleteModelViewSet):
    """CRUD for driving licence categories."""

    queryset = Category.objects.filter(is_active=True).order_by("name")
    serializer_class = CategorySerializer

    def create(self, request, *args, **kwargs):
        if not is_admin_or_superuser(request.user):
            return Response(
                {"detail": "Kategoriya yaratish faqat admin va superuser uchun ruxsat etilgan."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().create(request, *args, **kwargs)


# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------

class UserViewSet(SoftDeleteModelViewSet):
    """CRUD for system users (staff/instructors/etc.)."""

    queryset = User.objects.filter(is_active=True).order_by("phone")
    serializer_class = UserSerializer

    @action(detail=False, methods=["get"])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        if not (request.user and (request.user.is_superuser or request.user.role == User.Role.SUPERUSER)):
            return Response(
                {"detail": "Faqat superuser foydalanuvchi yaratishi mumkin."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if not (request.user and (request.user.is_superuser or request.user.role == User.Role.SUPERUSER)):
            return Response(
                {"detail": "Faqat superuser foydalanuvchini tahrirlashi mumkin."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        if not (request.user and (request.user.is_superuser or request.user.role == User.Role.SUPERUSER)):
            return Response(
                {"detail": "Faqat superuser foydalanuvchini tahrirlashi mumkin."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if not (request.user and (request.user.is_superuser or request.user.role == User.Role.SUPERUSER)):
            return Response(
                {"detail": "Faqat superuser foydalanuvchini o'chirishi mumkin."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)


# ---------------------------------------------------------------------------
# Student
# ---------------------------------------------------------------------------

class StudentViewSet(SoftDeleteModelViewSet):
    """CRUD for driving school students."""

    queryset = Student.objects.filter(is_active=True).order_by("full_name")
    serializer_class = StudentSerializer
    pagination_class = StandardPagination

    def get_serializer_class(self):
        if self.action == "create":
            return StudentCreateSerializer
        return StudentSerializer

    def create(self, request, *args, **kwargs):
        if not is_admin_or_superuser(request.user):
            return Response(
                {"detail": "O'quvchini ro'yxatdan o'tkazish faqat admin va superuser uchun ruxsat etilgan."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().create(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get("category")
        status = self.request.query_params.get("status")
        search = self.request.query_params.get("search")
        jshshr = self.request.query_params.get("jshshr")

        if category:
            if category.isdigit():
                queryset = queryset.filter(enrollments__category_id=category, enrollments__is_active=True)
            else:
                queryset = queryset.filter(enrollments__category__name=category, enrollments__is_active=True)
        if status:
            status_map = {
                'Yangi': Enrollment.Status.NEW,
                'Qabul qilingan': Enrollment.Status.ENROLLED,
                'Tugatgan': Enrollment.Status.FINISHED,
            }
            mapped_status = status_map.get(status, status)
            queryset = queryset.filter(enrollments__status=mapped_status, enrollments__is_active=True)
        if search:
            from django.db.models import Q
            queryset = queryset.filter(Q(full_name__icontains=search) | Q(phone__icontains=search) | Q(phone2__icontains=search))
        if jshshr:
            queryset = queryset.filter(jshshr__icontains=jshshr)

        return queryset.distinct()


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
    pagination_class = StandardPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.query_params.get("status")
        method = self.request.query_params.get("method")
        category = self.request.query_params.get("category")
        student_name = self.request.query_params.get("student_name")
        jshshr = self.request.query_params.get("jshshr")
        date_from = self.request.query_params.get("date_from")
        date_to = self.request.query_params.get("date_to")

        if status:
            queryset = queryset.filter(status=status)
        if method:
            queryset = queryset.filter(method=method)
        if category:
            if category.isdigit():
                queryset = queryset.filter(enrollment__category_id=category)
            else:
                queryset = queryset.filter(enrollment__category__name=category)
        if student_name:
            queryset = queryset.filter(enrollment__student__full_name__icontains=student_name)
        if jshshr:
            queryset = queryset.filter(enrollment__student__jshshr__icontains=jshshr)
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=f"{date_to} 23:59:59.999999")

        return queryset

    def create(self, request, *args, **kwargs):
        if not is_admin_or_superuser(request.user):
            return Response(
                {"detail": "To'lovni qabul qilish faqat admin va superuser uchun ruxsat etilgan."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if not (request.user and (request.user.is_superuser or request.user.role == User.Role.SUPERUSER)):
            return Response(
                {"detail": "Faqat superuser to'lov ma'lumotlarini tahrirlashi mumkin."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        if not (request.user and (request.user.is_superuser or request.user.role == User.Role.SUPERUSER)):
            return Response(
                {"detail": "Faqat superuser to'lov ma'lumotlarini tahrirlashi mumkin."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if not (request.user and (request.user.is_superuser or request.user.role == User.Role.SUPERUSER)):
            return Response(
                {"detail": "Faqat superuser to'lov ma'lumotlarini tahrirlashi mumkin."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)


# ---------------------------------------------------------------------------
# Group
# ---------------------------------------------------------------------------

class GroupViewSet(SoftDeleteModelViewSet):
    """CRUD for groups of students."""

    queryset = Group.objects.filter(is_active=True).order_by("-created_at")
    serializer_class = GroupSerializer

    def create(self, request, *args, **kwargs):
        if not is_admin_or_superuser(request.user):
            return Response(
                {"detail": "Guruh yaratish faqat admin va superuser uchun ruxsat etilgan."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().create(request, *args, **kwargs)


# ---------------------------------------------------------------------------
# LearningPlace
# ---------------------------------------------------------------------------

class LearningPlaceViewSet(SoftDeleteModelViewSet):
    """CRUD for physical / online learning places."""

    queryset = LearningPlace.objects.filter(is_active=True).order_by("-created_at")
    serializer_class = LearningPlaceSerializer

    def create(self, request, *args, **kwargs):
        if not is_admin_or_superuser(request.user):
            return Response(
                {"detail": "O'quv joyi yaratish faqat admin va superuser uchun ruxsat etilgan."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().create(request, *args, **kwargs)

