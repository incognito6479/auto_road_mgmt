"""
management/views.py

All application views for the Driving School Management app live here.
"""

from django.core.exceptions import FieldDoesNotExist
from django.db.models import Q
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from management.models import Branch, Category, User, Enrollment, Payment, Group, LearningPlace, Agent, Holidays, Car, CarWash, DrivingLessons, Notification, TeacherReview, StudentCertificate
from management.serializers import (
    BranchSerializer,
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
    CarWashSerializer,
    DrivingLessonsSerializer,
    NotificationSerializer,
    TeacherReviewSerializer,
    StudentCertificateSerializer,
)


# ---------------------------------------------------------------------------
# Base viewset: soft-delete (sets is_active=False instead of deleting) +
# automatic branch assignment on create
# ---------------------------------------------------------------------------

def _model_has_own_branch_field(model):
    """True if `model` declares its own `branch` ForeignKey (not a reverse relation)."""
    try:
        field = model._meta.get_field("branch")
    except FieldDoesNotExist:
        return False
    return getattr(field, "many_to_one", False)


class SoftDeleteModelViewSet(viewsets.ModelViewSet):
    """
    A ModelViewSet where `destroy` performs a soft-delete:
    sets `is_active = False` on the instance instead of removing it from the DB.

    Also auto-assigns `branch` on create for any model that has that field:
    superusers may pass an explicit `branch` in the payload (this is how the
    navbar branch selector stamps new records), defaulting to their own branch
    if omitted; every other role is always forced to their own assigned
    branch, regardless of what the client sends.
    """

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save(update_fields=["is_active"])
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        model = getattr(getattr(serializer, "Meta", None), "model", None)
        if model is None or not _model_has_own_branch_field(model):
            serializer.save()
            return

        user = self.request.user
        is_super = bool(
            user and user.is_authenticated and (user.is_superuser or user.role == User.Role.SUPERUSER)
        )

        if is_super:
            raw_branch = None
            if hasattr(self.request.data, "get"):
                raw_branch = self.request.data.get("branch")
            if raw_branch not in (None, "", "null"):
                try:
                    serializer.save(branch_id=int(raw_branch))
                    return
                except (TypeError, ValueError):
                    pass
            if getattr(user, "branch_id", None):
                serializer.save(branch_id=user.branch_id)
                return
            serializer.save()
            return

        # Non-superusers: always their own branch, client value ignored entirely.
        serializer.save(branch_id=getattr(user, "branch_id", None))


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


def is_superuser(user):
    if not user or not user.is_authenticated:
        return False
    return user.is_superuser or user.role == User.Role.SUPERUSER


def get_scoped_branch_value(request):
    """
    Returns the branch filter value ("id" as str, branch name, a sentinel for
    "no branch assigned", or None for "no restriction") that should be applied
    to this request.

    Only superusers may switch branches via the `?branch=` query param. Every
    other role is locked to their own assigned branch regardless of what the
    client sends.
    """
    user = getattr(request, "user", None)
    is_super = bool(
        user and user.is_authenticated and (user.is_superuser or user.role == User.Role.SUPERUSER)
    )
    if is_super:
        return request.query_params.get("branch")

    if user and user.is_authenticated and user.branch_id:
        return str(user.branch_id)

    # Authenticated but has no branch assigned: only branch-less rows are visible.
    return "__none__"


def filter_by_branch(queryset, request, branch_field="branch"):
    branch = get_scoped_branch_value(request)
    if branch == "__none__":
        kw_null = {f"{branch_field}__isnull": True}
        return queryset.filter(Q(**kw_null))
    if branch:
        if branch.isdigit():
            kw_id = {f"{branch_field}_id": branch}
            kw_null = {f"{branch_field}__isnull": True}
            queryset = queryset.filter(Q(**kw_id) | Q(**kw_null))
        else:
            kw_name = {f"{branch_field}__name__iexact": branch.strip()}
            kw_null = {f"{branch_field}__isnull": True}
            queryset = queryset.filter(Q(**kw_name) | Q(**kw_null))
    return queryset


# ---------------------------------------------------------------------------
# Branch
# ---------------------------------------------------------------------------

class BranchViewSet(SoftDeleteModelViewSet):
    """CRUD for branches / filials."""

    queryset = Branch.objects.filter(is_active=True).order_by("-updated_at", "-created_at")
    serializer_class = BranchSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(name__icontains=search.strip())
        return qs


# ---------------------------------------------------------------------------
# Holidays
# ---------------------------------------------------------------------------

class HolidaysViewSet(SoftDeleteModelViewSet):
    """CRUD for holidays and official days off."""

    queryset = Holidays.objects.filter(is_active=True).order_by("-updated_at", "-created_at")
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

    queryset = Category.objects.filter(is_active=True).order_by("-updated_at", "-created_at")
    serializer_class = CategorySerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        qs = super().get_queryset()
        return filter_by_branch(qs, self.request, "branch")

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

    queryset = User.objects.filter(is_active=True).order_by("-date_joined")
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
        return filter_by_branch(qs, self.request, "branch")

    @action(detail=False, methods=["get"])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=["post"], url_path="change-password")
    def change_password(self, request):
        """Lets any authenticated user set a new password for themself."""
        new_password = request.data.get("new_password")

        if not new_password:
            return Response(
                {"detail": "Yangi parolni kiriting."},
                status=status.HTTP_400_BAD_REQUEST
            )
        if len(new_password) < 4:
            return Response(
                {"detail": "Yangi parol kamida 4 ta belgidan iborat bo'lishi kerak."},
                status=status.HTTP_400_BAD_REQUEST
            )

        request.user.set_password(new_password)
        request.user.save(update_fields=["password"])
        return Response({"detail": "Parol muvaffaqiyatli o'zgartirildi."})

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

    queryset = User.objects.filter(role=User.Role.STUDENT, is_active=True).order_by("-date_joined")
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

    def update(self, request, *args, **kwargs):
        if not is_admin_or_superuser(request.user):
            return Response(
                {"detail": "O'quvchini tahrirlash faqat admin va superuser uchun ruxsat etilgan."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        if not is_admin_or_superuser(request.user):
            return Response(
                {"detail": "O'quvchini tahrirlash faqat admin va superuser uchun ruxsat etilgan."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().partial_update(request, *args, **kwargs)

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
                'Faol': Enrollment.Status.ENROLLED,
                'Tugatgan': Enrollment.Status.FINISHED,
                'Bekor qilingan': Enrollment.Status.CANCELED,
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

        queryset = filter_by_branch(queryset, self.request, "branch")
        return queryset.distinct()


# ---------------------------------------------------------------------------
# Enrollment
# ---------------------------------------------------------------------------

class EnrollmentViewSet(SoftDeleteModelViewSet):
    """CRUD for student enrollments."""

    queryset = Enrollment.objects.filter(is_active=True).order_by("-updated_at", "-created_at")
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
        learning_place = self.request.query_params.get("learning_place")

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
        if learning_place:
            queryset = queryset.filter(learning_place_id=learning_place)
        return filter_by_branch(queryset, self.request, "branch")


# ---------------------------------------------------------------------------
# Payment
# ---------------------------------------------------------------------------

class PaymentViewSet(SoftDeleteModelViewSet):
    """CRUD for student payments."""

    queryset = Payment.objects.filter(is_active=True).order_by("-updated_at", "-created_at")
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
        user_param = self.request.query_params.get("user")

        if enrollment:
            queryset = queryset.filter(enrollment_id=enrollment)
        if student:
            queryset = queryset.filter(enrollment__student_id=student)
        if user_param:
            queryset = queryset.filter(user_id=user_param)
        if agent:
            queryset = queryset.filter(Q(agent_id=agent) | Q(enrollment__agent_id=agent))
        if status:
            if "," in status:
                queryset = queryset.filter(status__in=[s.strip() for s in status.split(",") if s.strip()])
            else:
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
                Q(enrollment__category__name__icontains=student_name) |
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

        branch = get_scoped_branch_value(self.request)
        if branch == "__none__":
            queryset = queryset.filter(Q(branch__isnull=True) & Q(enrollment__branch__isnull=True))
        elif branch:
            if branch.isdigit():
                queryset = queryset.filter(Q(branch_id=branch) | Q(enrollment__branch_id=branch) | Q(branch__isnull=True))
            else:
                queryset = queryset.filter(Q(branch__name__iexact=branch.strip()) | Q(enrollment__branch__name__iexact=branch.strip()) | Q(branch__isnull=True))

        return queryset

    def create(self, request, *args, **kwargs):
        if not is_admin_or_superuser(request.user):
            return Response(
                {"detail": "To'lovni qabul qilish faqat admin va superuser uchun ruxsat etilgan."},
                status=status.HTTP_403_FORBIDDEN
            )
        # Returning money is a superuser-only operation — admins may record
        # every other kind of payment but never hand money back.
        if request.data.get("status") == Payment.Status.RETURNED and not is_superuser(request.user):
            return Response(
                {"detail": "Pulni qaytarish faqat superuser uchun ruxsat etilgan."},
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

    @action(detail=True, methods=["post"], url_path="pay-bonus")
    def pay_bonus(self, request, pk=None):
        """
        Fills in the real amount on a placeholder bonus_teacher payment
        (created at amount=0 when the certificate was uploaded).
        """
        payment = self.get_object()
        if not is_admin_or_superuser(request.user):
            return Response(
                {"detail": "Faqat admin va superuser bonus to'lashi mumkin."},
                status=status.HTTP_403_FORBIDDEN
            )
        if payment.status != Payment.Status.BONUS_TEACHER:
            return Response(
                {"detail": "Bu to'lov o'qituvchi bonusi emas."},
                status=status.HTTP_400_BAD_REQUEST
            )
        if payment.amount > 0:
            return Response(
                {"detail": "Ushbu bonus allaqachon to'langan."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            amount = int(request.data.get("amount"))
            if amount <= 0:
                raise ValueError
        except (TypeError, ValueError):
            return Response({"detail": "To'g'ri summa kiriting."}, status=status.HTTP_400_BAD_REQUEST)

        payment.amount = amount
        payment.method = request.data.get("method", payment.method)
        if request.data.get("notes"):
            payment.notes = request.data.get("notes")
        payment.save(update_fields=["amount", "method", "notes", "updated_at"])

        return Response(PaymentSerializer(payment, context={"request": request}).data)


# ---------------------------------------------------------------------------
# Group
# ---------------------------------------------------------------------------

class GroupViewSet(SoftDeleteModelViewSet):
    """CRUD for groups of students."""

    queryset = Group.objects.filter(is_active=True).order_by("-updated_at", "-created_at")
    serializer_class = GroupSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        qs = super().get_queryset()
        return filter_by_branch(qs, self.request, "branch")

    def create(self, request, *args, **kwargs):
        if not is_admin_or_superuser(request.user):
            return Response(
                {"detail": "Guruh yaratish faqat admin va superuser uchun ruxsat etilgan."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if not is_admin_or_superuser(request.user):
            return Response(
                {"detail": "Guruhni tahrirlash faqat admin va superuser uchun ruxsat etilgan."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        if not is_admin_or_superuser(request.user):
            return Response(
                {"detail": "Guruhni tahrirlash faqat admin va superuser uchun ruxsat etilgan."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().partial_update(request, *args, **kwargs)


# ---------------------------------------------------------------------------
# LearningPlace
# ---------------------------------------------------------------------------

class LearningPlaceViewSet(SoftDeleteModelViewSet):
    """CRUD for physical / online learning places."""

    queryset = LearningPlace.objects.filter(is_active=True).order_by("-updated_at", "-created_at")
    serializer_class = LearningPlaceSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        qs = super().get_queryset()
        return filter_by_branch(qs, self.request, "branch")

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

    queryset = Agent.objects.filter(is_active=True).order_by("-updated_at", "-created_at")
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
        return filter_by_branch(qs, self.request, "branch")

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

    queryset = Car.objects.filter(is_active=True).order_by("-updated_at", "-created_at")
    serializer_class = CarSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        car_name = self.request.query_params.get("car_name") or self.request.query_params.get("search")
        status_param = self.request.query_params.get("status")
        instructor_param = self.request.query_params.get("instructor")
        if car_name:
            queryset = queryset.filter(car_name__icontains=car_name)
        if status_param:
            queryset = queryset.filter(status=status_param)
        if instructor_param:
            queryset = queryset.filter(instructor_id=instructor_param)
        return queryset

    @action(detail=True, methods=["post"])
    def mark_washed(self, request, pk=None):
        """
        Marks this car as washed. The car's currently assigned instructor,
        any mechanic, or an admin/superuser may do this. `washed_at` is
        always the server's current time — any date/time sent by the client
        is ignored, so a wash can never be backdated.
        """
        car = self.get_object()
        user = request.user

        is_assigned_instructor = bool(
            user and user.is_authenticated and car.instructor_id and user.id == car.instructor_id
        )
        is_mechanic = bool(user and user.is_authenticated and user.role == User.Role.MECHANIC)
        if not (is_assigned_instructor or is_mechanic or is_admin_or_superuser(user)):
            return Response(
                {"detail": "Faqat ushbu avtomobilga biriktirilgan instruktor, mexanik yoki admin uni yuvilgan deb belgilashi mumkin."},
                status=status.HTTP_403_FORBIDDEN
            )

        wash = CarWash.objects.create(car=car, instructor_id=car.instructor_id, washed_at=timezone.now())
        car.last_washed_at = wash.washed_at
        car.save(update_fields=["last_washed_at", "updated_at"])

        return Response(CarWashSerializer(wash).data, status=status.HTTP_201_CREATED)


# ---------------------------------------------------------------------------
# DrivingLessons
# ---------------------------------------------------------------------------

class DrivingLessonsViewSet(SoftDeleteModelViewSet):
    """CRUD for driving lesson confirmations."""

    queryset = DrivingLessons.objects.filter(is_active=True).order_by("-updated_at", "-created_at")
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
        return filter_by_branch(qs, self.request, "branch")


# ---------------------------------------------------------------------------
# Notification
# ---------------------------------------------------------------------------

class NotificationViewSet(SoftDeleteModelViewSet):
    """CRUD & Actions for notifications."""

    queryset = Notification.objects.filter(is_active=True).order_by("-updated_at", "-created_at")
    serializer_class = NotificationSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        qs = super().get_queryset()
        status_param = self.request.query_params.get("status")
        is_read_param = self.request.query_params.get("is_read")

        if status_param:
            qs = qs.filter(status=status_param)
        if is_read_param is not None:
            is_read_bool = is_read_param.lower() in ["true", "1"]
            qs = qs.filter(is_read=is_read_bool)

        # Every notification is scoped to whoever is asking: admins/superusers
        # see their own plus any "for admins" broadcast (user is null) rows —
        # e.g. new review or certificate-upload alerts — while everyone else
        # only ever sees notifications addressed directly to them.
        user = self.request.user
        if user and user.is_authenticated:
            if is_admin_or_superuser(user):
                qs = qs.filter(Q(user_id=user.id) | Q(user__isnull=True))
            else:
                qs = qs.filter(user_id=user.id)
        else:
            qs = qs.none()

        return filter_by_branch(qs, self.request, "branch")

    @action(detail=False, methods=["get"])
    def unread_count(self, request):
        """Returns total unread count for notifications."""
        user = request.user if request.user and request.user.is_authenticated else None
        qs = Notification.objects.filter(is_active=True, is_read=False)
        if user:
            if is_admin_or_superuser(user):
                qs = qs.filter(Q(user=user) | Q(user__isnull=True))
            else:
                qs = qs.filter(user=user)
        else:
            qs = qs.none()
        qs = filter_by_branch(qs, request, "branch")
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
        """Mark all of the requesting user's unread notifications as read."""
        user = request.user if request.user and request.user.is_authenticated else None
        qs = Notification.objects.filter(is_active=True, is_read=False)
        if user:
            if is_admin_or_superuser(user):
                qs = qs.filter(Q(user=user) | Q(user__isnull=True))
            else:
                qs = qs.filter(user=user)
        else:
            qs = qs.none()
        qs.update(is_read=True)
        return Response({"status": "all marked as read"})


# ---------------------------------------------------------------------------
# TeacherReview
# ---------------------------------------------------------------------------

class TeacherReviewViewSet(SoftDeleteModelViewSet):
    """Reviews students leave for their coordinator/instructor."""

    queryset = TeacherReview.objects.filter(is_active=True).order_by("-updated_at", "-created_at")
    serializer_class = TeacherReviewSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        qs = super().get_queryset()
        student = self.request.query_params.get("student")
        teacher = self.request.query_params.get("teacher")
        if student:
            qs = qs.filter(student_id=student)
        if teacher:
            qs = qs.filter(teacher_id=teacher)
        return filter_by_branch(qs, self.request, "branch")

    def create(self, request, *args, **kwargs):
        user = request.user
        if not (user and user.is_authenticated):
            return Response(
                {"detail": "Avtorizatsiyadan o'ting."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        teacher_id = request.data.get("teacher")
        if teacher_id and str(teacher_id) == str(user.id):
            return Response(
                {"detail": "O'zingizga sharh qoldira olmaysiz."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        user = self.request.user
        review = serializer.save(student=user, branch_id=getattr(user, "branch_id", None))

        # Notify admins/superusers only — this Notification has no `user` set,
        # so NotificationViewSet's queryset only surfaces it to admin/superuser.
        teacher_label = review.teacher.full_name or review.teacher.phone
        student_label = review.student.full_name or review.student.phone
        Notification.objects.create(
            title=f"Yangi sharh: {student_label} → {teacher_label}",
            note=review.comment or f"Baho: {review.rating}/5",
            status=Notification.Status.REVIEW,
            target_id=review.teacher_id,
            user=None,
            branch=None,
        )


# ---------------------------------------------------------------------------
# StudentCertificate
# ---------------------------------------------------------------------------

class StudentCertificateViewSet(SoftDeleteModelViewSet):
    """Certificates instructors upload for a specific student."""

    queryset = StudentCertificate.objects.filter(is_active=True).order_by("-updated_at", "-created_at")
    serializer_class = StudentCertificateSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        qs = super().get_queryset()
        student = self.request.query_params.get("student")
        instructor = self.request.query_params.get("instructor")
        if student:
            qs = qs.filter(student_id=student)
        if instructor:
            qs = qs.filter(instructor_id=instructor)
        return filter_by_branch(qs, self.request, "branch")

    def create(self, request, *args, **kwargs):
        user = request.user
        if not (user and user.is_authenticated and user.role != User.Role.STUDENT):
            return Response(
                {"detail": "O'quvchilar sertifikat yuklay olmaydi."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        user = self.request.user
        student = serializer.validated_data.get("student")
        enrollment = student.enrollments.filter(is_active=True).first() if student else None

        if user.role == User.Role.INSTRUCTOR:
            instructor = user
        else:
            # Uploader isn't the instructor themself (e.g. admin/coordinator) —
            # fall back to the student's currently assigned instructor, if any.
            instructor = enrollment.instructor if (enrollment and enrollment.instructor) else None
        cert = serializer.save(instructor=instructor, branch_id=getattr(user, "branch_id", None), is_active=True)

        student_label = cert.student.full_name or cert.student.phone
        instructor_label = cert.instructor.full_name if cert.instructor else (user.full_name or user.phone)

        # A zero-amount placeholder bonus payment is created right away so it
        # shows up in the teachers' finance view as "awaiting payment" — an
        # admin/superuser later fills in the real amount via pay_bonus.
        if instructor:
            payment = Payment.objects.create(
                user=instructor,
                enrollment=enrollment,
                amount=0,
                status=Payment.Status.BONUS_TEACHER,
                method=Payment.Method.CASH,
                branch=cert.branch,
                notes=f"Sertifikat bonusi: {student_label}",
            )
            cert.bonus_payment = payment
            cert.save(update_fields=["bonus_payment", "updated_at"])

        Notification.objects.create(
            title=f"Yangi sertifikat yuklandi: {student_label}",
            note=f"Yuklagan: {instructor_label}",
            status=Notification.Status.CERTIFICATE_UPLOAD,
            target_id=cert.student_id,
            user=None,
            branch=None,
        )


