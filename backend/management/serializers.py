"""
management/serializers.py

DRF serializers for all management models.
"""

from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.db.models import Sum

from datetime import timedelta
from management.models import Branch, Category, User, Enrollment, Payment, Group, LearningPlace, Agent, Holidays, Car, CarAssignmentHistory, CarWash, DrivingLessons, AutodromeAccessGrant, Notification, TeacherReview, StudentCertificate, Attendance


_NOT_CACHED = object()


def get_current_student_enrollment(student):
    """
    The enrollment that represents a student's *current* state — always the
    most recently created active enrollment, never an arbitrary one. A
    student can accumulate multiple enrollments over time (e.g. re-enrolling
    after being canceled, or switching category), so picking anything but
    the latest risks showing a stale status/category/group/instructor that
    no longer reflects reality — and, worse, disagreeing with whichever
    enrollment a status-tab filter elsewhere matched on for the same student.

    StudentSerializer calls this once per output field (17 separate
    SerializerMethodFields) — without caching, listing every student
    (page_size=100000, as StudentsView does) turned into tens of thousands
    of near-duplicate queries and made the page hang indefinitely. The
    result is cached on the student instance itself, so repeat calls for the
    same row are free; this is safe because each request loads fresh model
    instances from the DB, so there's no cross-request staleness.

    If StudentViewSet.get_queryset already prefetched each student's active
    enrollments (current_enrollment_list, newest first), the first call
    resolves entirely from memory — no query at all. Otherwise (a single
    student fetched some other way) it falls back to one indexed query.
    """
    cached = getattr(student, "_current_enrollment_cache", _NOT_CACHED)
    if cached is not _NOT_CACHED:
        return cached
    prefetched = getattr(student, "current_enrollment_list", None)
    if prefetched is not None:
        enrollment = prefetched[0] if prefetched else None
    else:
        enrollment = student.enrollments.filter(is_active=True).select_related(
            "category", "instructor", "coordinator", "agent", "group"
        ).order_by("-created_at", "-id").first()
    student._current_enrollment_cache = enrollment
    return enrollment


def ensure_phone_is_unique(value, instance=None):
    """
    `phone` is the login identifier (USERNAME_FIELD), but the model only
    enforces uniqueness across ("phone", "jshshr"). Two people sharing a phone
    therefore passes model validation and then breaks authentication outright:
    the auth backend does a `.get(phone=...)` and raises MultipleObjectsReturned,
    which surfaces as a 500 for *both* accounts on that number. Reject the
    duplicate up front instead.

    Pass `instance` on updates so a record doesn't collide with itself.
    """
    if not value:
        return value
    qs = User.objects.filter(phone=value)
    if instance is not None and instance.pk is not None:
        qs = qs.exclude(pk=instance.pk)
    if qs.exists():
        raise serializers.ValidationError(
            "Bu telefon raqami allaqachon ro'yxatdan o'tgan. "
            "Har bir foydalanuvchi uchun telefon raqami takrorlanmasligi kerak."
        )
    return value


def compute_group_schedule(started_at, working_days, selected_weekdays=None, working_weekends_choice=None):
    """
    Walks forward day-by-day from `started_at`, counting only days that are
    an actual class day (a selected weekday, per `selected_weekdays` or the
    legacy `working_weekends_choice`) and not a holiday, until `working_days`
    such days have been counted.

    Returns `(duration_months, ends_at)`:
      - `ends_at` is the calendar date of the last counted class day. Since
        every skipped holiday and non-class weekday between `started_at` and
        `ends_at` extends the span by one day, this is equivalent to
        `started_at + working_days + (holidays in range) + (off-weekdays in range)`.
      - `duration_months` is that same span expressed in ~30-day months, kept
        for backward-compatible display purposes.

    `selected_weekdays` (preferred going forward): list of ints, 0=Mon .. 5=Sat
    (Sunday is never a class day). Falls back to the legacy `working_weekends`
    enum (everyday / mon-wed-fri / tue-thu-sat) when not provided, for groups
    created before the weekday picker existed.
    """
    if not started_at or not working_days or working_days <= 0:
        return None, None

    # Active holidays
    holiday_ranges = list(Holidays.objects.filter(is_active=True).values_list("start_date", "end_date"))

    def is_holiday(dt):
        for s_date, e_date in holiday_ranges:
            if s_date <= dt <= e_date:
                return True
        return False

    if selected_weekdays:
        weekday_set = {int(d) for d in selected_weekdays if str(d).lstrip("-").isdigit() and 0 <= int(d) <= 5}

        def is_working_day(dt):
            return dt.weekday() in weekday_set
    else:
        def is_working_day(dt):
            wd = dt.weekday()  # 0 = Mon, ..., 6 = Sun
            if working_weekends_choice == Group.WorkingWeekends.EVERYDAY:
                return wd != 6  # Monday through Saturday (Sunday excluded)
            elif working_weekends_choice == Group.WorkingWeekends.MWF:
                return wd in (0, 2, 4)  # Mon, Wed, Fri
            elif working_weekends_choice == Group.WorkingWeekends.TTS:
                return wd in (1, 3, 5)  # Tue, Thu, Sat
            return wd != 6

    curr = started_at
    count = 0
    while count < working_days:
        if is_working_day(curr) and not is_holiday(curr):
            count += 1
        if count == working_days:
            break
        curr += timedelta(days=1)

    cal_days = (curr - started_at).days + 1
    duration_months = round(cal_days / 30.0, 1)
    return duration_months, curr


# ---------------------------------------------------------------------------
# Holidays
# ---------------------------------------------------------------------------

class HolidaysSerializer(serializers.ModelSerializer):
    class Meta:
        model = Holidays
        fields = [
            "id",
            "holiday_name",
            "start_date",
            "end_date",
            "note",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "is_active", "created_at", "updated_at"]



# ---------------------------------------------------------------------------
# Branch
# ---------------------------------------------------------------------------

class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = ["id", "name", "notes", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "is_active", "created_at", "updated_at"]


# ---------------------------------------------------------------------------
# Category
# ---------------------------------------------------------------------------

class CategorySerializer(serializers.ModelSerializer):
    registered = serializers.SerializerMethodField()
    branch_name = serializers.CharField(source="branch.name", read_only=True)

    class Meta:
        model = Category
        fields = ["id", "name", "price", "duration", "branch", "branch_name", "is_active", "registered", "notes", "created_at", "updated_at"]
        read_only_fields = ["id", "is_active", "created_at", "updated_at"]

    def get_registered(self, obj):
        return User.objects.filter(
            role=User.Role.STUDENT,
            enrollments__category=obj,
            enrollments__is_active=True,
            enrollments__status=Enrollment.Status.NEW
        ).count()


# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------

class UserSerializer(serializers.ModelSerializer):
    """
    General-purpose user serializer for all system users (including students).
    `password` is write-only: accepted on create/update, never returned.
    """

    branch_name = serializers.CharField(source="branch.name", read_only=True)
    password = serializers.CharField(
        write_only=True,
        required=False,
        style={"input_type": "password"},
    )

    full_name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    phone2 = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    jshshr = serializers.IntegerField(required=False, allow_null=True)
    passport_serie = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    passport_number = serializers.IntegerField(required=False, allow_null=True)
    license_series = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    license_number = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    certificate_series = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    certificate_number = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = User
        fields = [
            "id",
            "phone",
            "phone2",
            "role",
            "first_name",
            "last_name",
            "full_name",
            "email",
            "image",
            "pass_img",
            "branch",
            "branch_name",
            "jshshr",
            "passport_serie",
            "passport_number",
            "license_series",
            "license_number",
            "certificate_series",
            "certificate_number",
            "certificate_added_date",
            "notes",
            "password",
            "is_active",
            "is_staff",
            "is_superuser",
            "date_joined",
        ]
        read_only_fields = ["id", "is_active", "date_joined", "certificate_added_date"]
        extra_kwargs = {
            "password": {"write_only": True, "required": False},
            "jshshr": {"required": False, "allow_null": True},
            "passport_serie": {"required": False, "allow_blank": True, "allow_null": True},
            "passport_number": {"required": False, "allow_null": True},
        }

    def validate_phone(self, value):
        return ensure_phone_is_unique(value, self.instance)

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        # certificate_added_date is server-controlled: stamp it the moment
        # certificate info is first entered, never accept a client value.
        if user.certificate_series or user.certificate_number:
            user.certificate_added_date = timezone.now()
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        cert_series_before = instance.certificate_series
        cert_number_before = instance.certificate_number
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        # certificate_added_date is server-controlled — recompute it whenever
        # certificate_series/certificate_number actually changed, so no client
        # can backdate/forward-date it via the request payload.
        if instance.certificate_series != cert_series_before or instance.certificate_number != cert_number_before:
            instance.certificate_added_date = timezone.now() if (instance.certificate_series or instance.certificate_number) else None
        instance.save()
        return instance


# ---------------------------------------------------------------------------
# Student (User model with role=STUDENT)
# ---------------------------------------------------------------------------

class StudentSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    category = serializers.SerializerMethodField()
    category_id = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    payment_amount = serializers.SerializerMethodField()
    enrolled_free = serializers.SerializerMethodField()
    instructor = serializers.SerializerMethodField()
    instructor_name = serializers.SerializerMethodField()
    coordinator = serializers.SerializerMethodField()
    coordinator_name = serializers.SerializerMethodField()
    agent = serializers.SerializerMethodField()
    agent_name = serializers.SerializerMethodField()
    learning_time = serializers.SerializerMethodField()
    learning_days = serializers.SerializerMethodField()
    group = serializers.SerializerMethodField()
    group_name = serializers.SerializerMethodField()
    group_started_at = serializers.SerializerMethodField()
    group_ends_at = serializers.SerializerMethodField()
    branch_name = serializers.CharField(source="branch.name", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "full_name",
            "first_name",
            "last_name",
            "phone",
            "phone2",
            "image",
            "pass_img",
            "branch",
            "branch_name",
            "jshshr",
            "passport_serie",
            "passport_number",
            "birth_date",
            "certificate_series",
            "certificate_number",
            "certificate_added_date",
            "status",
            "category",
            "category_id",
            "instructor",
            "instructor_name",
            "coordinator",
            "coordinator_name",
            "agent",
            "agent_name",
            "learning_time",
            "learning_days",
            "group",
            "group_name",
            "group_started_at",
            "group_ends_at",
            "payment_amount",
            "enrolled_free",
            "notes",
            "is_active",
            "date_joined",
        ]
        read_only_fields = ["id", "is_active", "date_joined", "certificate_added_date"]

    def get_category(self, obj):
        enrollment = get_current_student_enrollment(obj)
        return enrollment.category.name if enrollment else None

    def get_category_id(self, obj):
        enrollment = get_current_student_enrollment(obj)
        return enrollment.category.id if enrollment else None

    def get_status(self, obj):
        enrollment = get_current_student_enrollment(obj)
        return enrollment.status if enrollment else None

    def get_enrolled_free(self, obj):
        enrollment = get_current_student_enrollment(obj)
        return enrollment.enrolled_free if enrollment else False

    def get_instructor(self, obj):
        enrollment = get_current_student_enrollment(obj)
        return enrollment.instructor_id if enrollment else None

    def get_instructor_name(self, obj):
        enrollment = get_current_student_enrollment(obj)
        return enrollment.instructor.full_name if (enrollment and enrollment.instructor) else None

    def get_coordinator(self, obj):
        enrollment = get_current_student_enrollment(obj)
        return enrollment.coordinator_id if enrollment else None

    def get_coordinator_name(self, obj):
        enrollment = get_current_student_enrollment(obj)
        return enrollment.coordinator.full_name if (enrollment and enrollment.coordinator) else None

    def get_agent(self, obj):
        enrollment = get_current_student_enrollment(obj)
        return enrollment.agent_id if enrollment else None

    def get_agent_name(self, obj):
        enrollment = get_current_student_enrollment(obj)
        return enrollment.agent.full_name if (enrollment and enrollment.agent) else None

    def get_learning_time(self, obj):
        enrollment = get_current_student_enrollment(obj)
        return enrollment.learning_time if enrollment else None

    def get_learning_days(self, obj):
        enrollment = get_current_student_enrollment(obj)
        return enrollment.learning_days if enrollment else []

    def get_group(self, obj):
        enrollment = get_current_student_enrollment(obj)
        return enrollment.group_id if enrollment else None

    def get_group_name(self, obj):
        enrollment = get_current_student_enrollment(obj)
        return enrollment.group.name if (enrollment and enrollment.group) else None

    def get_group_started_at(self, obj):
        enrollment = get_current_student_enrollment(obj)
        return enrollment.group.started_at if (enrollment and enrollment.group) else None

    def get_group_ends_at(self, obj):
        enrollment = get_current_student_enrollment(obj)
        return enrollment.group.ends_at if (enrollment and enrollment.group) else None

    def get_payment_amount(self, obj):
        # `student_payment_amount_agg` is a queryset-level annotation (see
        # StudentViewSet.get_queryset) that replaces a per-row Payment
        # aggregate query with one computed for the whole list; instances
        # that didn't come from that queryset (e.g. a single create/update
        # response) fall back to the direct per-row query.
        if hasattr(obj, "student_payment_amount_agg"):
            return obj.student_payment_amount_agg or 0
        enrollment = get_current_student_enrollment(obj)
        if not enrollment:
            return 0
        result = enrollment.payments.filter(is_active=True).aggregate(total=Sum("amount"))
        return result["total"] or 0

    def validate_phone(self, value):
        return ensure_phone_is_unique(value, self.instance)

    def update(self, instance, validated_data):
        full_name = self.context.get("request").data.get("full_name") if self.context.get("request") else None
        if full_name is not None:
            parts = full_name.strip().split(" ", 1)
            instance.first_name = parts[0] if len(parts) > 0 else ""
            instance.last_name = parts[1] if len(parts) > 1 else ""

        request = self.context.get("request")
        category_id = request.data.get("category") if request else None
        status_val = request.data.get("status") if request else None
        instructor_id = request.data.get("instructor") if request else None
        coordinator_id = request.data.get("coordinator") if request else None
        agent_id = request.data.get("agent") if request else None
        learning_time = request.data.get("learning_time") if request else None
        learning_days = request.data.get("learning_days") if request else None

        # Students sign in with phone + JSHSHR, so the password has to follow the
        # JSHSHR whenever it is edited. Without this the account silently keeps
        # the old JSHSHR as its password and the student can no longer log in.
        old_jshshr = instance.jshshr
        cert_series_before = instance.certificate_series
        cert_number_before = instance.certificate_number

        with transaction.atomic():
            student = super().update(instance, validated_data)

            # certificate_added_date is server-controlled — recompute it
            # whenever certificate_series/certificate_number actually changed,
            # so no client can backdate/forward-date it via the request payload.
            if student.certificate_series != cert_series_before or student.certificate_number != cert_number_before:
                student.certificate_added_date = timezone.now() if (student.certificate_series or student.certificate_number) else None
                student.save(update_fields=["certificate_added_date"])

            if student.jshshr and student.jshshr != old_jshshr:
                student.set_password(str(student.jshshr))
                student.save(update_fields=["password"])

            enrollment = get_current_student_enrollment(student)
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
                if instructor_id is not None:
                    enrollment.instructor_id = instructor_id or None
                if coordinator_id is not None:
                    enrollment.coordinator_id = coordinator_id or None
                if agent_id is not None:
                    enrollment.agent_id = agent_id or None
                if learning_time is not None:
                    enrollment.learning_time = learning_time or None
                if learning_days is not None:
                    enrollment.learning_days = learning_days
                enrollment.save()
            else:
                if category_id:
                    try:
                        category = Category.objects.get(id=category_id, is_active=True)
                        new_enrollment = Enrollment.objects.create(
                            student=student,
                            category=category,
                            branch_id=student.branch_id,
                            status=status_val or Enrollment.Status.NEW,
                            instructor_id=instructor_id or None,
                            coordinator_id=coordinator_id or None,
                            agent_id=agent_id or None,
                            learning_time=learning_time or None,
                            learning_days=learning_days or [],
                        )
                        # get_current_student_enrollment cached "no enrollment"
                        # for this student a few lines up — refresh it so the
                        # response this serializer builds next reflects the
                        # enrollment just created instead of that stale miss.
                        student._current_enrollment_cache = new_enrollment
                    except Category.DoesNotExist:
                        pass
        return student


class StudentCreateSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(write_only=True)
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.filter(is_active=True),
        write_only=True,
    )
    instructor = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role=User.Role.INSTRUCTOR, is_active=True),
        write_only=True,
        required=False,
        allow_null=True,
    )
    coordinator = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role=User.Role.COORDINATOR, is_active=True),
        write_only=True,
        required=False,
        allow_null=True,
    )
    agent = serializers.PrimaryKeyRelatedField(
        queryset=Agent.objects.filter(is_active=True),
        write_only=True,
        required=False,
        allow_null=True,
    )
    min_payment = serializers.IntegerField(
        write_only=True,
        min_value=0,
    )
    status = serializers.ChoiceField(
        choices=Enrollment.Status.choices,
        default=Enrollment.Status.NEW,
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
    can_view_payments = serializers.BooleanField(
        write_only=True,
        default=True,
    )
    learning_place = serializers.PrimaryKeyRelatedField(
        queryset=LearningPlace.objects.filter(is_active=True),
        write_only=True,
        required=False,
        allow_null=True,
    )
    learning_time = serializers.CharField(
        write_only=True,
        required=False,
        allow_null=True,
        allow_blank=True,
    )
    learning_days = serializers.ListField(
        child=serializers.IntegerField(min_value=0, max_value=5),
        write_only=True,
        required=False,
        default=list,
    )
    payment_method = serializers.ChoiceField(
        choices=Payment.Method.choices,
        default=Payment.Method.CASH,
        write_only=True,
        required=False,
    )
    payment_amount = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "full_name",
            "phone",
            "phone2",
            "image",
            "pass_img",
            "jshshr",
            "passport_serie",
            "passport_number",
            "birth_date",
            "status",
            "category",
            "instructor",
            "coordinator",
            "agent",
            "learning_place",
            "learning_time",
            "learning_days",
            "min_payment",
            "payment_method",
            "enrolled_free",
            "enrolled_amount",
            "can_view_payments",
            "payment_amount",
        ]
        read_only_fields = ["id", "payment_amount"]

    def validate_phone(self, value):
        return ensure_phone_is_unique(value, self.instance)

    def get_payment_amount(self, obj):
        enrollment = get_current_student_enrollment(obj)
        if not enrollment:
            return 0
        result = enrollment.payments.filter(is_active=True).aggregate(total=Sum("amount"))
        return result["total"] or 0

    def create(self, validated_data):
        full_name = validated_data.pop("full_name", "")
        parts = full_name.strip().split(" ", 1)
        first_name = parts[0] if len(parts) > 0 else ""
        last_name = parts[1] if len(parts) > 1 else ""

        category = validated_data.pop("category")
        instructor = validated_data.pop("instructor", None)
        coordinator = validated_data.pop("coordinator", None)
        agent = validated_data.pop("agent", None)
        learning_place = validated_data.pop("learning_place", None)
        learning_time = validated_data.pop("learning_time", None)
        learning_days = validated_data.pop("learning_days", None)
        min_payment = validated_data.pop("min_payment")
        payment_method = validated_data.pop("payment_method", Payment.Method.CASH)
        enrollment_status = validated_data.pop("status", Enrollment.Status.NEW)
        enrolled_free = validated_data.pop("enrolled_free", False)
        enrolled_amount = validated_data.pop("enrolled_amount", None)
        can_view_payments = validated_data.pop("can_view_payments", True)

        if enrolled_free:
            enrolled_amount = 0
        elif enrolled_amount is None:
            enrolled_amount = category.price
        
        request = self.context.get("request")
        cashier = request.user if request else None

        with transaction.atomic():
            jshshr_val = validated_data.get("jshshr")
            student = User(
                role=User.Role.STUDENT,
                full_name=full_name,
                first_name=first_name,
                last_name=last_name,
                **validated_data
            )
            if jshshr_val:
                student.set_password(str(jshshr_val))
            student.save()

            # Create Enrollment (inherits the student's branch)
            enrollment = Enrollment.objects.create(
                student=student,
                category=category,
                branch_id=student.branch_id,
                instructor=instructor,
                coordinator=coordinator,
                agent=agent,
                learning_place=learning_place,
                learning_time=learning_time,
                learning_days=learning_days,
                status=enrollment_status,
                enrolled_free=enrolled_free,
                enrolled_amount=enrolled_amount,
                can_view_payments=can_view_payments,
            )

            # Create Payment (inherits the student's branch)
            if min_payment and min_payment > 0:
                Payment.objects.create(
                    user=cashier,
                    enrollment=enrollment,
                    branch_id=student.branch_id,
                    amount=min_payment,
                    status=Payment.Status.ACCEPTED,
                    method=payment_method,
                )

        return student


class AgentSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source="branch.name", read_only=True)
    # A "teacher agent" — an instructor/coordinator who brought in a student
    # themselves and earns the referral bonus like any other agent. When
    # `user` is set, full_name/phone are no longer typed in by hand; they're
    # snapshotted from the linked user instead (see validate() below).
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role__in=[User.Role.INSTRUCTOR, User.Role.COORDINATOR], is_active=True),
        required=False,
        allow_null=True,
    )
    user_name = serializers.CharField(source="user.full_name", read_only=True)
    user_role = serializers.CharField(source="user.role", read_only=True)
    full_name = serializers.CharField(required=False, allow_blank=True)
    phone = serializers.CharField(
        required=False, allow_blank=True,
        validators=[UniqueValidator(queryset=Agent.objects.all(), message="Ushbu telefon raqamli agent allaqachon mavjud.")],
    )

    class Meta:
        model = Agent
        fields = [
            "id",
            "full_name",
            "phone",
            "phone2",
            "user",
            "user_name",
            "user_role",
            "branch",
            "branch_name",
            "notes",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "is_active", "created_at", "updated_at"]

    def validate(self, attrs):
        user = attrs.get("user", getattr(self.instance, "user", None))
        if user:
            attrs["full_name"] = user.full_name or ""
            attrs["phone"] = user.phone
        else:
            full_name = attrs.get("full_name", getattr(self.instance, "full_name", None))
            phone = attrs.get("phone", getattr(self.instance, "phone", None))
            if not full_name:
                raise serializers.ValidationError({"full_name": "Agent F.I.SH. kiritilishi shart."})
            if not phone:
                raise serializers.ValidationError({"phone": "Telefon raqami kiritilishi shart."})
        return attrs


class LearningPlaceSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source="branch.name", read_only=True)

    class Meta:
        model = LearningPlace
        fields = ["id", "place_name", "branch", "branch_name", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "is_active", "created_at", "updated_at"]


class EnrollmentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.full_name", read_only=True)
    student_phone = serializers.CharField(source="student.phone", read_only=True)
    student_phone2 = serializers.CharField(source="student.phone2", read_only=True)
    student_jshshr = serializers.CharField(source="student.jshshr", read_only=True)
    student_certificate_series = serializers.CharField(source="student.certificate_series", read_only=True)
    student_certificate_number = serializers.CharField(source="student.certificate_number", read_only=True)
    student_certificate_added_date = serializers.DateTimeField(source="student.certificate_added_date", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)
    group_name = serializers.CharField(source="group.name", read_only=True)
    instructor_name = serializers.SerializerMethodField()
    coordinator_name = serializers.SerializerMethodField()
    agent_name = serializers.CharField(source="agent.full_name", read_only=True)
    agent_phone = serializers.CharField(source="agent.phone", read_only=True)
    learning_place_name = serializers.CharField(source="learning_place.place_name", read_only=True)
    paid_amount = serializers.SerializerMethodField()
    branch_name = serializers.CharField(source="branch.name", read_only=True)

    class Meta:
        model = Enrollment
        fields = [
            "id", "student", "student_name", "student_phone", "student_phone2", "student_jshshr",
            "student_certificate_series", "student_certificate_number", "student_certificate_added_date",
            "category", "category_name", "group", "group_name", "instructor", "instructor_name", "coordinator", "coordinator_name",
            "agent", "agent_name", "agent_phone",
            "learning_place", "learning_place_name", "learning_time", "learning_days", "status",
            "enrolled_free", "enrolled_amount", "can_view_payments", "excel_imported", "paid_amount", "branch", "branch_name", "notes",
            "is_active", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "is_active", "created_at", "updated_at"]

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
        # `paid_amount_agg` is a queryset-level annotation (see
        # Enrollment.objects_with_paid_amount / callers in views.py) that
        # computes this via a correlated subquery in the same SQL query as
        # the enrollment list, instead of one extra query per row — use it
        # whenever the queryset was built that way, and only fall back to
        # the per-row aggregate for the rare unannotated path (e.g. a
        # single freshly created/updated instance handed back by DRF's
        # default create/update, which never re-queries via get_queryset).
        if hasattr(obj, "paid_amount_agg"):
            return obj.paid_amount_agg or 0
        result = obj.payments.filter(status="accepted", is_active=True).aggregate(total=Sum("amount"))
        return result["total"] or 0


class PaymentSerializer(serializers.ModelSerializer):
    student = serializers.IntegerField(source="enrollment.student.id", read_only=True, default=None)
    student_name = serializers.CharField(source="enrollment.student.full_name", read_only=True)
    student_jshshr = serializers.CharField(source="enrollment.student.jshshr", read_only=True)
    category = serializers.IntegerField(source="enrollment.category.id", read_only=True)
    category_id = serializers.IntegerField(source="enrollment.category.id", read_only=True)
    category_name = serializers.CharField(source="enrollment.category.name", read_only=True)
    group = serializers.IntegerField(source="enrollment.group.id", read_only=True, default=None)
    group_name = serializers.CharField(source="enrollment.group.name", read_only=True, default=None)
    group_started_at = serializers.DateField(source="enrollment.group.started_at", read_only=True, default=None)
    group_ends_at = serializers.DateField(source="enrollment.group.ends_at", read_only=True, default=None)
    cashier_name = serializers.SerializerMethodField()
    user_full_name = serializers.CharField(source="user.full_name", read_only=True)
    user_phone = serializers.CharField(source="user.phone", read_only=True)
    user_phone2 = serializers.CharField(source="user.phone2", read_only=True)
    user_role = serializers.CharField(source="user.role", read_only=True)
    created_by_name = serializers.SerializerMethodField()
    agent_name = serializers.CharField(source="agent.full_name", read_only=True)
    agent_phone = serializers.CharField(source="agent.phone", read_only=True)
    agent_phone2 = serializers.CharField(source="agent.phone2", read_only=True)
    branch_name = serializers.CharField(source="branch.name", read_only=True)
    student_paid_amount = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = [
            "id", "user", "user_full_name", "user_phone", "user_phone2", "user_role", "cashier_name",
            "created_by", "created_by_name", "enrollment", "student", "student_name", "student_jshshr",
            "category", "category_id", "category_name", "group", "group_name", "group_started_at", "group_ends_at",
            "agent", "agent_name", "agent_phone", "agent_phone2", "branch", "branch_name",
            "amount", "status", "method", "click_check_image", "notes", "is_active", "created_at", "updated_at",
            "student_paid_amount",
        ]
        read_only_fields = ["id", "created_by", "is_active", "created_at", "updated_at"]

    def get_cashier_name(self, obj):
        user = obj.user
        if not user:
            return None
        return user.full_name or f"{user.first_name or ''} {user.last_name or ''}".strip() or user.phone

    def get_created_by_name(self, obj):
        user = obj.created_by
        if not user:
            return None
        return user.full_name or f"{user.first_name or ''} {user.last_name or ''}".strip() or user.phone

    def get_student_paid_amount(self, obj):
        if not obj.enrollment_id:
            return None
        # See PaymentViewSet.get_queryset — annotated in the same query as
        # the payment list itself; only falls back to the per-row aggregate
        # for an unannotated instance (e.g. straight off create/update).
        if hasattr(obj, "student_paid_amount_agg"):
            return obj.student_paid_amount_agg or 0
        result = obj.enrollment.payments.filter(status="accepted", is_active=True).aggregate(total=Sum("amount"))
        return result["total"] or 0


class GroupSerializer(serializers.ModelSerializer):
    student_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    student_count = serializers.SerializerMethodField()
    category_name = serializers.CharField(source="category.name", read_only=True)
    branch_name = serializers.CharField(source="branch.name", read_only=True)
    enrollments = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = [
            "id", "category", "category_name", "name", "started_at", "ends_at",
            "working_days", "working_weekends", "selected_weekdays", "duration", "status",
            "branch", "branch_name", "student_ids", "student_count", "enrollments", "notes",
            "is_active", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "is_active", "ends_at", "created_at", "updated_at", "student_count"]

    def get_student_count(self, obj):
        # len() reuses Group.enrollments' prefetch cache (set up in
        # GroupViewSet.get_queryset, retrieve only) when it's there;
        # otherwise .count() is a cheap SQL COUNT instead of pulling every
        # column of every row just to measure the list.
        if "enrollments" in getattr(obj, "_prefetched_objects_cache", {}):
            return len(obj.enrollments.all())
        return obj.enrollments.count()

    def get_enrollments(self, obj):
        # Every group's full member roster (each with its own several-FK
        # EnrollmentSerializer) is only actually used by GroupDetailView's
        # single-group fetch (?with_enrollments=1). Every other caller across
        # the app — list calls looking up started_at/ends_at by id, and
        # single-group fetches like StudentDetailView's that only read the
        # group's own fields — has no use for it, so skip serializing it
        # entirely rather than silently dragging along a full nested roster
        # (in the list case, up to page_size=1000 groups' worth) on a call
        # that never reads it.
        view = self.context.get("view")
        action = getattr(view, "action", None) if view is not None else None
        request = self.context.get("request")
        if action == "list":
            return []
        if action == "retrieve" and not (request and request.query_params.get("with_enrollments")):
            return []
        return EnrollmentSerializer(obj.enrollments.all(), many=True, context=self.context).data

    def create(self, validated_data):
        student_ids = validated_data.pop("student_ids", [])
        category = validated_data.get("category")
        working_days = validated_data.get("working_days")
        if not working_days and category:
            working_days = getattr(category, "duration", 68) or 68
            validated_data["working_days"] = working_days

        started_at = validated_data.get("started_at")
        selected_weekdays = validated_data.get("selected_weekdays")
        working_weekends = validated_data.get("working_weekends", Group.WorkingWeekends.MWF)
        if started_at and working_days:
            computed_dur, computed_end = compute_group_schedule(
                started_at, working_days, selected_weekdays, working_weekends
            )
            if computed_dur:
                validated_data["duration"] = computed_dur
            if computed_end:
                validated_data["ends_at"] = computed_end

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

    def update(self, instance, validated_data):
        category = validated_data.get("category", instance.category)
        working_days = validated_data.get(
            "working_days",
            instance.working_days or (getattr(category, "duration", 68) if category else 68)
        )
        validated_data["working_days"] = working_days

        started_at = validated_data.get("started_at", instance.started_at)
        selected_weekdays = validated_data.get("selected_weekdays", instance.selected_weekdays)
        working_weekends = validated_data.get("working_weekends", instance.working_weekends)

        if started_at and working_days:
            computed_dur, computed_end = compute_group_schedule(
                started_at, working_days, selected_weekdays, working_weekends
            )
            if computed_dur:
                validated_data["duration"] = computed_dur
            if computed_end:
                validated_data["ends_at"] = computed_end

        return super().update(instance, validated_data)


class CarAssignmentHistorySerializer(serializers.ModelSerializer):
    instructor_name = serializers.CharField(source="instructor.full_name", read_only=True)

    class Meta:
        model = CarAssignmentHistory
        fields = [
            "id", "instructor", "instructor_name", "assigned_at", "unassigned_at",
            "mileage_at_unassignment", "oil_change_date_at_unassignment", "oil_change_mileage_at_unassignment",
        ]
        read_only_fields = fields


class CarWashSerializer(serializers.ModelSerializer):
    instructor_name = serializers.CharField(source="instructor.full_name", read_only=True)

    class Meta:
        model = CarWash
        fields = ["id", "instructor", "instructor_name", "washed_at"]
        read_only_fields = fields


class CarSerializer(serializers.ModelSerializer):
    instructor = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role=User.Role.INSTRUCTOR, is_active=True),
        required=False,
        allow_null=True,
    )
    instructor_name = serializers.CharField(source="instructor.full_name", read_only=True)
    # Full history, newest first — populated by CarViewSet.perform_create/update
    # and the mark_washed action, never written to directly.
    assignment_history = CarAssignmentHistorySerializer(many=True, read_only=True)
    wash_history = CarWashSerializer(many=True, read_only=True)

    class Meta:
        model = Car
        fields = [
            "id", "car_name", "image", "manufact_year", "policy_date",
            "tech_inspection_date", "status", "instructor", "instructor_name",
            "mileage", "oil_change_date", "oil_change_mileage", "oil_change_interval_km", "last_washed_at",
            "assignment_history", "wash_history",
            "notes", "is_active", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "is_active", "last_washed_at", "created_at", "updated_at"]

    def create(self, validated_data):
        car = super().create(validated_data)
        if car.instructor_id:
            CarAssignmentHistory.objects.create(car=car, instructor_id=car.instructor_id)
        return car

    def update(self, instance, validated_data):
        old_instructor_id = instance.instructor_id
        instructor_field_present = "instructor" in validated_data
        new_instructor = validated_data.get("instructor")
        new_instructor_id = new_instructor.id if new_instructor else None

        # Snapshot the car's oil-service state as it stands before this update
        # is applied, so the outgoing instructor's history row reflects what
        # they handed the car over with.
        snapshot_mileage = instance.mileage
        snapshot_oil_change_date = instance.oil_change_date
        snapshot_oil_change_mileage = instance.oil_change_mileage

        car = super().update(instance, validated_data)

        if instructor_field_present and new_instructor_id != old_instructor_id:
            if old_instructor_id:
                CarAssignmentHistory.objects.filter(
                    car=car, instructor_id=old_instructor_id, unassigned_at__isnull=True
                ).update(
                    unassigned_at=timezone.now(),
                    mileage_at_unassignment=snapshot_mileage,
                    oil_change_date_at_unassignment=snapshot_oil_change_date,
                    oil_change_mileage_at_unassignment=snapshot_oil_change_mileage,
                )
            if new_instructor_id:
                CarAssignmentHistory.objects.create(car=car, instructor_id=new_instructor_id)

        return car


class DrivingLessonsSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.full_name", read_only=True)
    instructor_name = serializers.CharField(source="instructor.full_name", read_only=True)
    car_name = serializers.CharField(source="car.car_name", read_only=True)
    branch_name = serializers.CharField(source="branch.name", read_only=True)

    class Meta:
        model = DrivingLessons
        fields = [
            "id", "student", "student_name", "instructor", "instructor_name",
            "car", "car_name", "branch", "branch_name", "lesson_type", "hours",
            "lesson_date", "notes", "is_active", "created_at", "updated_at"
        ]
        # lesson_date is server-controlled (BaseModel.created_at-style auto
        # timestamp) — always the server's current time at creation, never a
        # client-supplied value, so a lesson/autodrome session can't be
        # backdated or postdated.
        read_only_fields = ["id", "lesson_date", "is_active", "created_at", "updated_at"]

    def validate(self, attrs):
        lesson_type = attrs.get("lesson_type", DrivingLessons.LessonType.DRIVING)
        if lesson_type == DrivingLessons.LessonType.AUTODROME:
            hours = attrs.get("hours")
            if not hours or hours < 1:
                raise serializers.ValidationError({"hours": "Avtodrom uchun soatlar sonini kiriting (1-6)."})
            if hours > DrivingLessons.AUTODROME_MAX_HOURS:
                raise serializers.ValidationError({"hours": f"Avtodrom uchun maksimal {DrivingLessons.AUTODROME_MAX_HOURS} soat ruxsat etilgan."})

            student = attrs.get("student") or getattr(self.instance, "student", None)
            existing = DrivingLessons.objects.filter(
                student=student,
                lesson_type=DrivingLessons.LessonType.AUTODROME,
                is_active=True,
            )
            if self.instance:
                existing = existing.exclude(pk=self.instance.pk)
            used = existing.aggregate(total=Sum("hours"))["total"] or 0

            # An admin/superuser may have granted this student extra visits
            # for a specific date range (once the base cap was hit or their
            # group finished) — that extra allowance is only in effect while
            # today falls within the grant's start/end date.
            today = timezone.localdate()
            extra = AutodromeAccessGrant.objects.filter(
                student=student, is_active=True, start_date__lte=today, end_date__gte=today,
            ).aggregate(total=Sum("visits"))["total"] or 0
            max_hours = DrivingLessons.AUTODROME_MAX_HOURS + extra

            if used + hours > max_hours:
                remaining = max(0, max_hours - used)
                raise serializers.ValidationError({
                    "hours": f"Jami avtodrom vaqti {max_hours} soatdan oshmasligi kerak. Qolgan: {remaining} soat."
                })
        return attrs


class AutodromeAccessGrantSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.full_name", read_only=True)
    granted_by_name = serializers.CharField(source="granted_by.full_name", read_only=True)
    branch_name = serializers.CharField(source="branch.name", read_only=True)

    class Meta:
        model = AutodromeAccessGrant
        fields = [
            "id", "student", "student_name", "granted_by", "granted_by_name",
            "branch", "branch_name", "visits", "start_date", "end_date",
            "notes", "is_active", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "granted_by", "is_active", "created_at", "updated_at"]

    def validate(self, attrs):
        start_date = attrs.get("start_date", getattr(self.instance, "start_date", None))
        end_date = attrs.get("end_date", getattr(self.instance, "end_date", None))
        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError({"end_date": "Tugash sanasi boshlanish sanasidan oldin bo'lishi mumkin emas."})
        return attrs


class NotificationSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.full_name", read_only=True)
    branch_name = serializers.CharField(source="branch.name", read_only=True)

    class Meta:
        model = Notification
        fields = [
            "id", "user", "user_name", "title", "date", "note", "is_read",
            "status", "target_id", "branch", "branch_name", "is_active", "created_at", "updated_at"
        ]
        # date is server-controlled — always the server's current time at
        # creation, never a client-supplied value.
        read_only_fields = ["id", "date", "is_active", "created_at", "updated_at"]


class TeacherReviewSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.full_name", read_only=True)
    student_image = serializers.FileField(source="student.image", read_only=True)
    teacher_name = serializers.CharField(source="teacher.full_name", read_only=True)
    teacher_role = serializers.CharField(source="teacher.role", read_only=True)
    branch_name = serializers.CharField(source="branch.name", read_only=True)

    class Meta:
        model = TeacherReview
        fields = [
            "id", "student", "student_name", "student_image", "teacher", "teacher_name", "teacher_role",
            "branch", "branch_name", "rating", "comment", "is_active", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "student", "branch", "is_active", "created_at", "updated_at"]

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Baho 1 dan 5 gacha bo'lishi kerak.")
        return value

    def validate_teacher(self, value):
        if value.role not in (User.Role.INSTRUCTOR, User.Role.COORDINATOR):
            raise serializers.ValidationError("Faqat instruktor yoki o'qituvchiga sharh qoldirish mumkin.")
        return value


class StudentCertificateSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.full_name", read_only=True)
    coordinator_name = serializers.CharField(source="coordinator.full_name", read_only=True)
    branch_name = serializers.CharField(source="branch.name", read_only=True)
    bonus_paid = serializers.SerializerMethodField()
    bonus_amount = serializers.SerializerMethodField()
    bonus_payment_user_name = serializers.SerializerMethodField()

    class Meta:
        model = StudentCertificate
        fields = [
            "id", "student", "student_name", "coordinator", "coordinator_name",
            "branch", "branch_name", "image", "notes", "bonus_payment",
            "bonus_paid", "bonus_amount", "bonus_payment_user_name", "is_active", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "coordinator", "branch", "bonus_payment", "is_active", "created_at", "updated_at"]

    def get_bonus_paid(self, obj):
        return bool(obj.bonus_payment_id and obj.bonus_payment.amount > 0)

    def get_bonus_amount(self, obj):
        return obj.bonus_payment.amount if obj.bonus_payment_id else None

    def get_bonus_payment_user_name(self, obj):
        # The teacher (coordinator) the bonus payment is attributed to —
        # shown in the pay-bonus modal alongside the student's name.
        if obj.bonus_payment_id and obj.bonus_payment.user_id:
            return obj.bonus_payment.user.full_name or obj.bonus_payment.user.phone
        return None


# ---------------------------------------------------------------------------
# Attendance
# ---------------------------------------------------------------------------

class AttendanceSerializer(serializers.ModelSerializer):
    student = serializers.IntegerField(source="enrollment.student_id", read_only=True)
    student_name = serializers.CharField(source="enrollment.student.full_name", read_only=True)
    marked_by_name = serializers.CharField(source="marked_by.full_name", read_only=True)
    category_name = serializers.CharField(source="enrollment.category.name", read_only=True, default=None)
    group = serializers.IntegerField(source="enrollment.group_id", read_only=True, default=None)
    group_name = serializers.CharField(source="enrollment.group.name", read_only=True, default=None)
    group_started_at = serializers.DateField(source="enrollment.group.started_at", read_only=True, default=None)
    group_ends_at = serializers.DateField(source="enrollment.group.ends_at", read_only=True, default=None)
    learning_place_name = serializers.CharField(source="enrollment.learning_place.place_name", read_only=True, default=None)
    learning_days = serializers.ListField(source="enrollment.learning_days", read_only=True, default=list)
    learning_time = serializers.CharField(source="enrollment.learning_time", read_only=True, default=None)
    agent = serializers.IntegerField(source="enrollment.agent_id", read_only=True, default=None)
    agent_name = serializers.CharField(source="enrollment.agent.full_name", read_only=True, default=None)
    instructor = serializers.IntegerField(source="enrollment.instructor_id", read_only=True, default=None)
    coordinator = serializers.IntegerField(source="enrollment.coordinator_id", read_only=True, default=None)
    instructor_name = serializers.SerializerMethodField()
    coordinator_name = serializers.SerializerMethodField()

    class Meta:
        model = Attendance
        fields = [
            "id", "enrollment", "student", "student_name", "category_name",
            "group", "group_name", "group_started_at", "group_ends_at",
            "learning_place_name", "learning_days", "learning_time",
            "instructor", "instructor_name", "coordinator", "coordinator_name",
            "agent", "agent_name",
            "date", "is_absent", "marked_by", "marked_by_name",
            "notes", "is_active", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "marked_by", "is_active", "created_at", "updated_at"]

    def get_instructor_name(self, obj):
        instructor = obj.enrollment.instructor if obj.enrollment_id else None
        if not instructor:
            return None
        name = f"{instructor.first_name} {instructor.last_name}".strip()
        return name or instructor.phone

    def get_coordinator_name(self, obj):
        coordinator = obj.enrollment.coordinator if obj.enrollment_id else None
        if not coordinator:
            return None
        name = f"{coordinator.first_name} {coordinator.last_name}".strip()
        return name or coordinator.phone


