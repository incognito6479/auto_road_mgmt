"""
management/serializers.py

DRF serializers for all management models.
"""

from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from django.db.models import Sum

from datetime import timedelta
from management.models import Branch, Category, User, Enrollment, Payment, Group, LearningPlace, Agent, Holidays, Car, CarAssignmentHistory, CarWash, DrivingLessons, Notification, TeacherReview, StudentCertificate


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
    certificate_series = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    certificate_number = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    certificate_added_date = serializers.DateTimeField(required=False, allow_null=True)

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
        read_only_fields = ["id", "is_active", "date_joined"]
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
        read_only_fields = ["id", "is_active", "date_joined"]

    def get_category(self, obj):
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

    def get_instructor(self, obj):
        enrollment = obj.enrollments.filter(is_active=True).first()
        return enrollment.instructor_id if enrollment else None

    def get_instructor_name(self, obj):
        enrollment = obj.enrollments.filter(is_active=True).first()
        return enrollment.instructor.full_name if (enrollment and enrollment.instructor) else None

    def get_coordinator(self, obj):
        enrollment = obj.enrollments.filter(is_active=True).first()
        return enrollment.coordinator_id if enrollment else None

    def get_coordinator_name(self, obj):
        enrollment = obj.enrollments.filter(is_active=True).first()
        return enrollment.coordinator.full_name if (enrollment and enrollment.coordinator) else None

    def get_agent(self, obj):
        enrollment = obj.enrollments.filter(is_active=True).first()
        return enrollment.agent_id if enrollment else None

    def get_agent_name(self, obj):
        enrollment = obj.enrollments.filter(is_active=True).first()
        return enrollment.agent.full_name if (enrollment and enrollment.agent) else None

    def get_learning_time(self, obj):
        enrollment = obj.enrollments.filter(is_active=True).first()
        return enrollment.learning_time if enrollment else None

    def get_learning_days(self, obj):
        enrollment = obj.enrollments.filter(is_active=True).first()
        return enrollment.learning_days if enrollment else []

    def get_group(self, obj):
        enrollment = obj.enrollments.filter(is_active=True).first()
        return enrollment.group_id if enrollment else None

    def get_group_name(self, obj):
        enrollment = obj.enrollments.filter(is_active=True).first()
        return enrollment.group.name if (enrollment and enrollment.group) else None

    def get_group_started_at(self, obj):
        enrollment = obj.enrollments.filter(is_active=True).first()
        return enrollment.group.started_at if (enrollment and enrollment.group) else None

    def get_group_ends_at(self, obj):
        enrollment = obj.enrollments.filter(is_active=True).first()
        return enrollment.group.ends_at if (enrollment and enrollment.group) else None

    def get_payment_amount(self, obj):
        enrollment = obj.enrollments.filter(is_active=True).first()
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

        with transaction.atomic():
            student = super().update(instance, validated_data)

            if student.jshshr and student.jshshr != old_jshshr:
                student.set_password(str(student.jshshr))
                student.save(update_fields=["password"])

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
                        Enrollment.objects.create(
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
            "payment_amount",
        ]
        read_only_fields = ["id", "payment_amount"]

    def validate_phone(self, value):
        return ensure_phone_is_unique(value, self.instance)

    def get_payment_amount(self, obj):
        enrollment = obj.enrollments.filter(is_active=True).first()
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

    class Meta:
        model = Agent
        fields = [
            "id",
            "full_name",
            "phone",
            "phone2",
            "branch",
            "branch_name",
            "notes",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "is_active", "created_at", "updated_at"]


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
            "enrolled_free", "enrolled_amount", "paid_amount", "branch", "branch_name", "notes",
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
        result = obj.payments.filter(status="accepted", is_active=True).aggregate(total=Sum("amount"))
        return result["total"] or 0


class PaymentSerializer(serializers.ModelSerializer):
    student = serializers.IntegerField(source="enrollment.student.id", read_only=True, default=None)
    student_name = serializers.CharField(source="enrollment.student.full_name", read_only=True)
    student_jshshr = serializers.CharField(source="enrollment.student.jshshr", read_only=True)
    category = serializers.IntegerField(source="enrollment.category.id", read_only=True)
    category_id = serializers.IntegerField(source="enrollment.category.id", read_only=True)
    category_name = serializers.CharField(source="enrollment.category.name", read_only=True)
    group_name = serializers.CharField(source="enrollment.group.name", read_only=True, default=None)
    group_started_at = serializers.DateField(source="enrollment.group.started_at", read_only=True, default=None)
    group_ends_at = serializers.DateField(source="enrollment.group.ends_at", read_only=True, default=None)
    cashier_name = serializers.SerializerMethodField()
    user_full_name = serializers.CharField(source="user.full_name", read_only=True)
    user_phone = serializers.CharField(source="user.phone", read_only=True)
    user_phone2 = serializers.CharField(source="user.phone2", read_only=True)
    user_role = serializers.CharField(source="user.role", read_only=True)
    agent_name = serializers.CharField(source="agent.full_name", read_only=True)
    agent_phone = serializers.CharField(source="agent.phone", read_only=True)
    agent_phone2 = serializers.CharField(source="agent.phone2", read_only=True)
    branch_name = serializers.CharField(source="branch.name", read_only=True)
    student_paid_amount = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = [
            "id", "user", "user_full_name", "user_phone", "user_phone2", "user_role", "cashier_name", "enrollment", "student", "student_name", "student_jshshr",
            "category", "category_id", "category_name", "group_name", "group_started_at", "group_ends_at",
            "agent", "agent_name", "agent_phone", "agent_phone2", "branch", "branch_name",
            "amount", "status", "method", "notes", "is_active", "created_at", "updated_at",
            "student_paid_amount",
        ]
        read_only_fields = ["id", "is_active", "created_at", "updated_at"]

    def get_cashier_name(self, obj):
        user = obj.user
        if not user:
            return None
        return user.full_name or f"{user.first_name or ''} {user.last_name or ''}".strip() or user.phone

    def get_student_paid_amount(self, obj):
        if not obj.enrollment_id:
            return None
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
    enrollments = EnrollmentSerializer(many=True, read_only=True)

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
        return obj.enrollments.count()

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
        read_only_fields = ["id", "is_active", "created_at", "updated_at"]

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
            if used + hours > DrivingLessons.AUTODROME_MAX_HOURS:
                remaining = max(0, DrivingLessons.AUTODROME_MAX_HOURS - used)
                raise serializers.ValidationError({
                    "hours": f"Jami avtodrom vaqti {DrivingLessons.AUTODROME_MAX_HOURS} soatdan oshmasligi kerak. Qolgan: {remaining} soat."
                })
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
        read_only_fields = ["id", "is_active", "created_at", "updated_at"]


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
    instructor_name = serializers.CharField(source="instructor.full_name", read_only=True)
    branch_name = serializers.CharField(source="branch.name", read_only=True)
    bonus_paid = serializers.SerializerMethodField()
    bonus_amount = serializers.SerializerMethodField()

    class Meta:
        model = StudentCertificate
        fields = [
            "id", "student", "student_name", "instructor", "instructor_name",
            "branch", "branch_name", "image", "notes", "bonus_payment",
            "bonus_paid", "bonus_amount", "is_active", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "instructor", "branch", "bonus_payment", "is_active", "created_at", "updated_at"]

    def get_bonus_paid(self, obj):
        return bool(obj.bonus_payment_id and obj.bonus_payment.amount > 0)

    def get_bonus_amount(self, obj):
        return obj.bonus_payment.amount if obj.bonus_payment_id else None


