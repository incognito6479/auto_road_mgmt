"""
management/serializers.py

DRF serializers for all management models.
"""

from django.db import transaction
from rest_framework import serializers
from django.db.models import Sum

from datetime import timedelta
from management.models import Category, User, Enrollment, Payment, Group, LearningPlace, Agent, Holidays


def compute_group_duration(started_at, working_days, working_weekends_choice):
    if not started_at or not working_days or working_days <= 0:
        return None
    
    # Active holidays
    holiday_ranges = list(Holidays.objects.filter(is_active=True).values_list("start_date", "end_date"))
    
    def is_holiday(dt):
        for s_date, e_date in holiday_ranges:
            if s_date <= dt <= e_date:
                return True
        return False

    def is_working_day(dt):
        wd = dt.weekday() # 0 = Mon, ..., 6 = Sun
        if working_weekends_choice == Group.WorkingWeekends.EVERYDAY:
            return wd != 6 # Monday through Saturday (Sunday excluded)
        elif working_weekends_choice == Group.WorkingWeekends.MWF:
            return wd in (0, 2, 4) # Mon, Wed, Fri
        elif working_weekends_choice == Group.WorkingWeekends.TTS:
            return wd in (1, 3, 5) or wd in (1, 2, 5) # Tue, Thu, Sat
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
    return duration_months


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
        read_only_fields = ["id", "created_at", "updated_at"]



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
            "jshshr",
            "passport_serie",
            "passport_number",
            "notes",
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
# Student (User model with role=STUDENT)
# ---------------------------------------------------------------------------

class StudentSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    category = serializers.SerializerMethodField()
    category_id = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    payment_amount = serializers.SerializerMethodField()
    enrolled_free = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "full_name",
            "first_name",
            "last_name",
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
            "date_joined",
        ]
        read_only_fields = ["id", "date_joined"]

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

    def get_payment_amount(self, obj):
        enrollment = obj.enrollments.filter(is_active=True).first()
        if not enrollment:
            return 0
        result = enrollment.payments.filter(is_active=True).aggregate(total=Sum("amount"))
        return result["total"] or 0

    def update(self, instance, validated_data):
        full_name = self.context.get("request").data.get("full_name") if self.context.get("request") else None
        if full_name is not None:
            parts = full_name.strip().split(" ", 1)
            instance.first_name = parts[0] if len(parts) > 0 else ""
            instance.last_name = parts[1] if len(parts) > 1 else ""

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
    learning_days = serializers.ChoiceField(
        choices=Enrollment.LearningDays.choices,
        write_only=True,
        required=False,
        allow_null=True,
        allow_blank=True,
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
        enrollment_status = validated_data.pop("status", Enrollment.Status.ENROLLED)
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

            # Create Enrollment
            enrollment = Enrollment.objects.create(
                student=student,
                category=category,
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

            # Create Payment
            if min_payment and min_payment > 0:
                Payment.objects.create(
                    user=cashier,
                    enrollment=enrollment,
                    amount=min_payment,
                    status=Payment.Status.ACCEPTED,
                    method=payment_method,
                )

        return student


class AgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agent
        fields = [
            "id",
            "full_name",
            "phone",
            "phone2",
            "notes",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


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
    category_name = serializers.CharField(source="category.name", read_only=True)
    group_name = serializers.CharField(source="group.name", read_only=True)
    instructor_name = serializers.SerializerMethodField()
    coordinator_name = serializers.SerializerMethodField()
    agent_name = serializers.CharField(source="agent.full_name", read_only=True)
    agent_phone = serializers.CharField(source="agent.phone", read_only=True)
    learning_place_name = serializers.CharField(source="learning_place.place_name", read_only=True)
    paid_amount = serializers.SerializerMethodField()

    class Meta:
        model = Enrollment
        fields = [
            "id", "student", "student_name", "student_phone", "student_phone2", "student_jshshr",
            "category", "category_name", "group", "group_name", "instructor", "instructor_name", "coordinator", "coordinator_name",
            "agent", "agent_name", "agent_phone",
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
    agent_name = serializers.CharField(source="agent.full_name", read_only=True)
    agent_phone = serializers.CharField(source="agent.phone", read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id", "user", "cashier_name", "enrollment", "student_name", "student_jshshr", "category_name",
            "agent", "agent_name", "agent_phone",
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
            "working_days", "working_weekends", "duration", "status",
            "student_ids", "student_count", "enrollments", "notes",
            "is_active", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "created_at", "updated_at", "student_count"]

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
        working_weekends = validated_data.get("working_weekends", Group.WorkingWeekends.MWF)
        if started_at and working_days:
            computed_dur = compute_group_duration(started_at, working_days, working_weekends)
            if computed_dur:
                validated_data["duration"] = computed_dur
        
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
        working_weekends = validated_data.get("working_weekends", instance.working_weekends)

        if started_at and working_days:
            computed_dur = compute_group_duration(started_at, working_days, working_weekends)
            if computed_dur:
                validated_data["duration"] = computed_dur

        return super().update(instance, validated_data)
