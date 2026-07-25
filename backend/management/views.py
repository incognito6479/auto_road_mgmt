"""
management/views.py

All application views for the Driving School Management app live here.
"""

from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from management.models import Category, User, Enrollment, Payment, Group, LearningPlace, Agent, Holidays, Car, DrivingLessons, Notification
from management.serializers import (
    CategorySerializer,
    StudentSerializer,
    UserSerializer,
    StudentCreateSerializer,
    EnrollmentSerializer,
    PaymentSerializer,
    GroupSerializer,
    LearningPlaceSerializer,
    AgentSerializer,
    HolidaysSerializer,
    CarSerializer,
    DrivingLessonsSerializer,
    NotificationSerializer,
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
    max_page_size = 1000


def is_admin_or_superuser(user):
    if not user or not user.is_authenticated:
        return False
    return user.is_superuser or user.role in [User.Role.ADMIN, User.Role.SUPERUSER]


# ---------------------------------------------------------------------------
# Holidays
# ---------------------------------------------------------------------------

class HolidaysViewSet(SoftDeleteModelViewSet):
    """CRUD for holidays and official days off."""

    queryset = Holidays.objects.filter(is_active=True).order_by("-start_date")
    serializer_class = HolidaysSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(holiday_name__icontains=search.strip())
        return qs

    def create(self, request, *args, **kwargs):
        if not is_admin_or_superuser(request.user):
            return Response(
                {"detail": "Bayram yaratish faqat admin va superuser uchun ruxsat etilgan."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().create(request, *args, **kwargs)


# ---------------------------------------------------------------------------
# Category
# ---------------------------------------------------------------------------

class CategoryViewSet(SoftDeleteModelViewSet):
    """CRUD for driving licence categories."""

    queryset = Category.objects.filter(is_active=True).order_by("name")
    serializer_class = CategorySerializer
    pagination_class = StandardPagination

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
    pagination_class = StandardPagination

    def get_queryset(self):
        qs = super().get_queryset()
        role = self.request.query_params.get("role")
        search = self.request.query_params.get("search")

        if role:
            qs = qs.filter(role=role)
        if search:
            qs = qs.filter(
                Q(full_name__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(phone__icontains=search)
            )
        return qs

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
# Student (User model with role=STUDENT)
# ---------------------------------------------------------------------------

class StudentViewSet(SoftDeleteModelViewSet):
    """CRUD for driving school students (User model with role=student)."""

    queryset = User.objects.filter(role=User.Role.STUDENT, is_active=True).order_by("first_name", "last_name")
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
        status_param = self.request.query_params.get("status")
        search = self.request.query_params.get("search")
        jshshr = self.request.query_params.get("jshshr")

        if category:
            if category.isdigit():
                queryset = queryset.filter(enrollments__category_id=category, enrollments__is_active=True)
            else:
                queryset = queryset.filter(enrollments__category__name=category, enrollments__is_active=True)
        if status_param:
            status_map = {
                'Yangi': Enrollment.Status.NEW,
                'Qabul qilingan': Enrollment.Status.ENROLLED,
                'Tugatgan': Enrollment.Status.FINISHED,
            }
            mapped_status = status_map.get(status_param, status_param)
            queryset = queryset.filter(enrollments__status=mapped_status, enrollments__is_active=True)
        if search:
            queryset = queryset.filter(
                Q(full_name__icontains=search) | 
                Q(first_name__icontains=search) | 
                Q(last_name__icontains=search) | 
                Q(phone__icontains=search) | 
                Q(phone2__icontains=search)
            )
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
    pagination_class = StandardPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        student = self.request.query_params.get("student")
        category = self.request.query_params.get("category")
        status = self.request.query_params.get("status")
        instructor = self.request.query_params.get("instructor")
        coordinator = self.request.query_params.get("coordinator")
        agent = self.request.query_params.get("agent")
        group = self.request.query_params.get("group")

        if student:
            queryset = queryset.filter(student_id=student)
        if category:
            queryset = queryset.filter(category_id=category)
        if status:
            queryset = queryset.filter(status=status)
        if instructor:
            queryset = queryset.filter(instructor_id=instructor)
        if coordinator:
            queryset = queryset.filter(coordinator_id=coordinator)
        if agent:
            queryset = queryset.filter(agent_id=agent)
        if group:
            queryset = queryset.filter(group_id=group)
        return queryset


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
        enrollment = self.request.query_params.get("enrollment")
        student = self.request.query_params.get("student")
        agent = self.request.query_params.get("agent")

        if enrollment:
            queryset = queryset.filter(enrollment_id=enrollment)
        if student:
            queryset = queryset.filter(enrollment__student_id=student)
        if agent:
            queryset = queryset.filter(Q(agent_id=agent) | Q(enrollment__agent_id=agent))
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
            queryset = queryset.filter(
                Q(enrollment__student__full_name__icontains=student_name) |
                Q(agent__full_name__icontains=student_name) |
                Q(user__first_name__icontains=student_name) |
                Q(user__last_name__icontains=student_name) |
                Q(notes__icontains=student_name)
            )
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
    pagination_class = StandardPagination

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
    pagination_class = StandardPagination

    def create(self, request, *args, **kwargs):
        if not is_admin_or_superuser(request.user):
            return Response(
                {"detail": "O'quv joyi yaratish faqat admin va superuser uchun ruxsat etilgan."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().create(request, *args, **kwargs)


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

class AgentViewSet(SoftDeleteModelViewSet):
    """CRUD for Agents (Student recruiters / referrals)."""

    queryset = Agent.objects.filter(is_active=True).order_by("-created_at")
    serializer_class = AgentSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.query_params.get("search", None)
        if search:
            search_cleaned = search.strip().lower()
            qs = qs.filter(
                Q(full_name__icontains=search_cleaned) |
                Q(phone__icontains=search_cleaned) |
                Q(phone2__icontains=search_cleaned)
            )
        return qs

    def create(self, request, *args, **kwargs):
        if not is_admin_or_superuser(request.user):
            return Response(
                {"detail": "Agent yaratish faqat admin va superuser uchun ruxsat etilgan."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().create(request, *args, **kwargs)


# ---------------------------------------------------------------------------
# Car
# ---------------------------------------------------------------------------

class CarViewSet(SoftDeleteModelViewSet):
    """CRUD for driving school vehicles."""

    queryset = Car.objects.filter(is_active=True).order_by("-created_at")
    serializer_class = CarSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        car_name = self.request.query_params.get("car_name") or self.request.query_params.get("search")
        status_param = self.request.query_params.get("status")
        if car_name:
            queryset = queryset.filter(car_name__icontains=car_name)
        if status_param:
            queryset = queryset.filter(status=status_param)
        return queryset


# ---------------------------------------------------------------------------
# DrivingLessons
# ---------------------------------------------------------------------------

class DrivingLessonsViewSet(SoftDeleteModelViewSet):
    """CRUD for driving lesson confirmations."""

    queryset = DrivingLessons.objects.filter(is_active=True).order_by("-lesson_date", "-created_at")
    serializer_class = DrivingLessonsSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        qs = super().get_queryset()
        student = self.request.query_params.get("student")
        instructor = self.request.query_params.get("instructor")
        car = self.request.query_params.get("car")
        if student:
            qs = qs.filter(student_id=student)
        if instructor:
            qs = qs.filter(instructor_id=instructor)
        if car:
            qs = qs.filter(car_id=car)
        return qs


# ---------------------------------------------------------------------------
# Notification
# ---------------------------------------------------------------------------

class NotificationViewSet(SoftDeleteModelViewSet):
    """CRUD & Actions for notifications."""

    queryset = Notification.objects.filter(is_active=True).order_by("-date", "-created_at")
    serializer_class = NotificationSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        qs = super().get_queryset()
        status_param = self.request.query_params.get("status")
        is_read_param = self.request.query_params.get("is_read")
        user_param = self.request.query_params.get("user")

        if status_param:
            qs = qs.filter(status=status_param)
        if is_read_param is not None:
            is_read_bool = is_read_param.lower() in ["true", "1"]
            qs = qs.filter(is_read=is_read_bool)
        if user_param:
            qs = qs.filter(Q(user_id=user_param) | Q(user__isnull=True))
        return qs

    @action(detail=False, methods=["get"])
    def unread_count(self, request):
        """Returns total unread count for notifications."""
        user = request.user if request.user and request.user.is_authenticated else None
        qs = Notification.objects.filter(is_active=True, is_read=False)
        if user and not (user.is_superuser or user.role in ["superuser", "admin"]):
            qs = qs.filter(Q(user=user) | Q(user__isnull=True))
        count = qs.count()
        return Response({"unread_count": count})

    @action(detail=True, methods=["post"])
    def mark_as_read(self, request, pk=None):
        """Mark single notification as read."""
        notif = self.get_object()
        notif.is_read = True
        notif.save(update_fields=["is_read", "updated_at"])
        return Response({"status": "marked as read", "is_read": True})

    @action(detail=False, methods=["post"])
    def mark_all_read(self, request):
        """Mark all unread notifications as read."""
        Notification.objects.filter(is_active=True, is_read=False).update(is_read=True)
        return Response({"status": "all marked as read"})


