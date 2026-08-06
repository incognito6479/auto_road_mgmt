from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    """Custom manager using phone as the unique identifier instead of username."""

    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError("Telefon raqami kiritilishi shart.")
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "superuser")
        extra_fields.setdefault("jshshr", 12)
        extra_fields.setdefault("passport_serie", "AA")
        extra_fields.setdefault("passport_number", 12)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser uchun is_staff=True bo'lishi shart.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser uchun is_superuser=True bo'lishi shart.")

        return self.create_user(phone, password, **extra_fields)


class BaseModel(models.Model):
    """Abstract base model inherited by all models except User."""

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, db_index=True)
    notes = models.TextField(blank=True, null=True, help_text="Qo'shimcha eslatmalar")

    class Meta:
        abstract = True


class Branch(BaseModel):
    """Branch / Filial model."""

    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Filial nomi",
    )

    director_full_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Filial rahbarining to'liq F.I.SH. (yo'l varaqasi va daftarcha kabi hujjatlarda ishlatiladi)",
    )

    class Meta:
        db_table = "branch"
        verbose_name = "Filial"
        verbose_name_plural = "Filiallar"
        ordering = ["name"]

    def __str__(self):
        return self.name


class User(AbstractUser):
    """
    Custom user model using phone number as the login identifier.
    Roles: superuser, admin, mechanic, instructor, coordinator, student.
    """

    class Role(models.TextChoices):
        SUPERUSER = "superuser", "Superuser"
        ADMIN = "admin", "Admin"
        MECHANIC = "mechanic", "Mexanik"
        INSTRUCTOR = "instructor", "Instruktor"
        COORDINATOR = "coordinator", "O'qituvchi"
        STUDENT = "student", "O'quvchi"

    # Remove username — phone is the login field
    username = None

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.COORDINATOR,
    )

    # Primary login identifier
    phone = models.CharField(
        max_length=20,
        help_text="Namuna: 998909009090",
    )

    phone2 = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Qo'shimcha telefon raqami, xohlasa qarindoshi nomi bilan (namuna: +998 90 900 90 90 amakisi)",
    )

    jshshr = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="Namuna: 29572006200016",
    )

    passport_serie = models.CharField(
        max_length=2,
        blank=True,
        null=True,
        help_text="Namuna: AB",
    )

    passport_number = models.IntegerField(
        null=True,
        blank=True,
        help_text="Namuna: 2275679",
    )

    birth_date = models.DateField(
        null=True,
        blank=True,
        help_text="Tug'ilgan sana (o'quvchilar uchun)",
    )

    license_series = models.CharField(
        max_length=2,
        blank=True,
        null=True,
        help_text="Instruktorlik guvohnomasi seriyasi (2 ta harf). Namuna: AB",
    )

    license_number = models.CharField(
        max_length=6,
        blank=True,
        null=True,
        help_text="Instruktorlik guvohnomasi raqami (6 ta raqam)",
    )

    certificate_series = models.CharField(
        max_length=2,
        blank=True,
        null=True,
        help_text="Kursni tugatganlik sertifikati seriyasi. Namuna: AB",
    )

    certificate_number = models.CharField(
        max_length=9,
        blank=True,
        null=True,
        help_text="Kursni tugatganlik sertifikati raqami (9 ta raqam). Bu imtihon sertifikati emas, faqat kursni tugatganlik sertifikati — qo'shilishi hech qanday holatni o'zgartirmaydi.",
    )

    certificate_added_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Kursni tugatganlik sertifikati qo'shilgan sana",
    )

    updated_at = models.DateTimeField(auto_now=True)

    full_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="To'liq ismi",
    )

    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Qo'shimcha eslatmalar",
    )

    image = models.FileField(
        upload_to="users/",
        blank=True,
        null=True,
        help_text="Foydalanuvchi rasmi",
    )

    pass_img = models.FileField(
        upload_to="passports/",
        blank=True,
        null=True,
        help_text="Pasport nusxasi / rasmi (faqat talabalar uchun)",
    )

    branch = models.ForeignKey(
        "Branch",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
    )

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        db_table = "user"
        verbose_name = "User"
        verbose_name_plural = "Users"
        unique_together = ["phone", "jshshr"]

    def save(self, *args, **kwargs):
        if not self.full_name and (self.first_name or self.last_name):
            self.full_name = f"{self.first_name or ''} {self.last_name or ''}".strip()
        elif self.full_name and not (self.first_name or self.last_name):
            parts = self.full_name.strip().split(" ", 1)
            self.first_name = parts[0] if len(parts) > 0 else ""
            self.last_name = parts[1] if len(parts) > 1 else ""
        if not self.password and self.jshshr:
            self.set_password(str(self.jshshr))

        if self.pk:
            # A replaced (or cleared) profile photo would otherwise leave
            # the previous file behind on disk forever — delete it once the
            # new one is confirmed different.
            old_image = User.objects.filter(pk=self.pk).values_list("image", flat=True).first()
            if old_image and old_image != self.image.name:
                self.image.storage.delete(old_image)

        super().save(*args, **kwargs)

    def __str__(self):
        name_str = self.full_name or f"{self.first_name or ''} {self.last_name or ''}".strip() or self.phone
        return f"{name_str} ({self.role})"


class Holidays(BaseModel):
    """Holidays and official days off."""

    holiday_name = models.CharField(
        max_length=255,
        help_text="Bayram / Dam olish kuni nomi",
    )
    start_date = models.DateField(
        help_text="Boshlanish sanasi",
    )
    end_date = models.DateField(
        help_text="Tugash sanasi",
    )
    note = models.TextField(
        blank=True,
        null=True,
        help_text="Qo'shimcha izoh",
    )

    class Meta:
        db_table = "holidays"
        verbose_name = "Bayram"
        verbose_name_plural = "Bayramlar"
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.holiday_name} ({self.start_date} - {self.end_date})"


class Category(BaseModel):
    """Driving license category (e.g. A, B, BC)."""

    branch = models.ForeignKey(
        "Branch",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="categories",
    )
    name = models.CharField(
        max_length=10,
        unique=True,
        help_text="Namuna: A, B, BC",
    )

    price = models.PositiveIntegerField(
        help_text="Namuna: 4500000",
    )

    duration = models.PositiveIntegerField(
        default=68,
        help_text="Ish kunlari (masalan: 68)",
    )

    class Meta:
        db_table = "category"
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Group(BaseModel):
    """Driving school group of students."""

    class Status(models.TextChoices):
        STARTED = "started", "Boshlangan"
        FINISHED = "finished", "Tugatgan"
        CANCELED = "canceled", "Bekor qilingan"

    class WorkingWeekends(models.TextChoices):
        EVERYDAY = "everyday", "Har kuni (Mon-Sat)"
        MWF = "mon-wed-fri", "Dushanba - Chorshanba - Juma (Mo-Wed-Fri)"
        TTS = "tue-wed-sat", "Seshanba - Payshanba - Shanba (Tue-Thu-Sat)"

    branch = models.ForeignKey(
        "Branch",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="groups",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="groups",
    )
    name = models.CharField(
        max_length=100,
        help_text="Guruh nomi",
    )
    started_at = models.DateField(
        null=True,
        blank=True,
        help_text="Boshlanish sanasi",
    )
    ends_at = models.DateField(
        null=True,
        blank=True,
        help_text="Tugash sanasi (avtomatik hisoblanadi: ish kunlari + bayramlar + dars bo'lmagan kunlar)",
    )
    working_days = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Ish kunlari soni (kategoriyadan olinadi)",
    )
    working_weekends = models.CharField(
        max_length=20,
        choices=WorkingWeekends.choices,
        default=WorkingWeekends.MWF,
        help_text="Dars kunlari jadvali (eski, selected_weekdays yo'q bo'lsa ishlatiladi)",
    )
    selected_weekdays = models.JSONField(
        default=list,
        blank=True,
        help_text="Dars kunlari, Dushanba-Shanba: 0=Dushanba, 1=Seshanba, 2=Chorshanba, 3=Payshanba, 4=Juma, 5=Shanba",
    )
    duration = models.FloatField(
        blank=True,
        null=True,
        help_text="Davomiyligi (oylar, masalan, 3.2 yoki 3.4)",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.STARTED,
    )

    class Meta:
        db_table = "group"
        verbose_name = "Guruh"
        verbose_name_plural = "Guruhlar"

    def __str__(self):
        return f"{self.name} ({self.category.name})"


class LearningPlace(BaseModel):
    """Physical or online learning place / location."""

    branch = models.ForeignKey(
        "Branch",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="learning_places",
    )
    place_name = models.CharField(max_length=255, help_text="O'quv joyi nomi")

    class Meta:
        db_table = "learning_place"
        verbose_name = "Learning Place"
        verbose_name_plural = "Learning Places"

    def __str__(self):
        return self.place_name


class Agent(BaseModel):
    """Agent model for student recruiters/referrals."""

    branch = models.ForeignKey(
        "Branch",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="agents",
    )
    full_name = models.CharField(max_length=255, help_text="Agent F.I.SH.")
    phone = models.CharField(max_length=20, unique=True, help_text="Telefon raqami")
    phone2 = models.CharField(max_length=20, blank=True, null=True, help_text="Qo'shimcha telefon raqami")
    user = models.OneToOneField(
        "User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={"role__in": ["instructor", "coordinator"]},
        related_name="agent_profile",
        help_text="Agar bu agent aslida talaba olib kelgan o'qituvchi/instruktor bo'lsa, shu foydalanuvchiga bog'lanadi",
    )

    class Meta:
        db_table = "agent"
        verbose_name = "Agent"
        verbose_name_plural = "Agentlar"

    def __str__(self):
        return f"{self.full_name} ({self.phone})"


class Enrollment(BaseModel):
    """Junction model: Student <-> Category within a Group context."""

    class Status(models.TextChoices):
        NEW = "new", "Yangi"
        ENROLLED = "enrolled", "Faol"
        FINISHED = "finished", "Tugatgan"
        CANCELED = "canceled", "Bekor qilingan"

    branch = models.ForeignKey(
        "Branch",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="enrollments",
    )
    student = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        limit_choices_to={"role": User.Role.STUDENT},
        related_name="enrollments",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="enrollments",
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="enrollments",
    )
    instructor = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        limit_choices_to={"role": User.Role.INSTRUCTOR},
        null=True,
        blank=True,
        related_name="instructor_enrollments",
    )
    coordinator = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        limit_choices_to={"role": User.Role.COORDINATOR},
        null=True,
        blank=True,
        related_name="coordinator_enrollments",
    )
    agent = models.ForeignKey(
        Agent,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="enrollments",
    )
    learning_place = models.ForeignKey(
        LearningPlace,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="enrollments",
    )
    learning_time = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Masalan: 09:00",
    )
    learning_days = models.JSONField(
        default=list,
        blank=True,
        help_text="Dars kunlari, Dushanba-Shanba: 0=Dushanba, 1=Seshanba, 2=Chorshanba, 3=Payshanba, 4=Juma, 5=Shanba",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
    )
    enrolled_free = models.BooleanField(
        default=False,
        help_text="Bepul o'qish (grant yoki boshqa imtiyoz)",
    )
    enrolled_amount = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Shartnoma summasi",
    )
    can_view_payments = models.BooleanField(
        default=True,
        blank=True,
        null=True,
        help_text="O'quvchi o'z to'lovlar tarixini ko'ra oladimi",
    )
    excel_imported = models.BooleanField(
        default=False,
        help_text="Excel fayl orqali import qilingan yozuv (shartnoma summasi bo'sh bo'lishi mumkin)",
    )

    class Meta:
        db_table = "enrollment"
        verbose_name = "Enrollment"
        verbose_name_plural = "Enrollments"

    def __str__(self):
        return f"{self.student.full_name} - {self.category.name} ({self.status})"


class Payment(BaseModel):
    """Payment made by/for a student."""

    class Status(models.TextChoices):
        ACCEPTED = "accepted", "Qabul qilingan"
        RETURNED = "returned", "Qaytarilgan"
        PAID = "paid", "To'langan"
        BONUS = "bonus", "Bonus"
        BANK = "bank", "Bank"
        BONUS_TEACHER = "bonus_teacher", "Sertifikat bonusi"

    class Method(models.TextChoices):
        CASH = "cash", "Naqd"
        CARD = "card", "Karta"
        QR_CODE = "qr_code", "QR code"
        TRANSFER = "transfer", "O'tkazma"
        CLICK = "click", "Click"

    branch = models.ForeignKey(
        "Branch",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="payments",
        help_text="Payment's counterpart per status: cashier who accepted/returned/banked it, "
                   "the agent-bonus payout's cashier, or the teacher/instructor being paid.",
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="recorded_payments",
        help_text="The admin/superuser who entered this payment record into the system — "
                   "distinct from 'user', which means different things per status.",
    )
    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="payments",
    )
    agent = models.ForeignKey(
        "Agent",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments",
    )
    amount = models.PositiveIntegerField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACCEPTED,
    )
    method = models.CharField(
        max_length=20,
        choices=Method.choices,
        default=Method.CASH,
    )
    click_check_image = models.FileField(
        upload_to="click_checks/",
        blank=True,
        null=True,
        help_text="Click orqali to'langanda, to'lov cheki rasmi (ixtiyoriy)",
    )

    class Meta:
        db_table = "payment"
        verbose_name = "To'lov"
        verbose_name_plural = "To'lovlar"

    def __str__(self):
        student_name = self.enrollment.student.full_name if (self.enrollment and self.enrollment.student) else 'No Student'
        return f"{student_name} - {self.amount} ({self.status})"


class Car(BaseModel):
    """Driving school vehicle model."""

    class Status(models.TextChoices):
        AVAILABLE = "available", "Mavjud"
        REPAIRING = "repairing", "Ta'mirlashda"
        NOT_AVAILABLE = "not_available", "Mavjud emas"

    car_name = models.CharField(
        max_length=255,
        help_text="Avtomobil nomi va davlat raqami (masalan: Cobalt 01 A 777 AA)",
    )
    image = models.FileField(
        upload_to="cars/",
        blank=True,
        null=True,
        help_text="Avtomobil rasmi",
    )
    manufact_year = models.IntegerField(
        null=True,
        blank=True,
        help_text="Ishlab chiqarilgan yili (masalan: 2022)",
    )
    policy_date = models.DateField(
        null=True,
        blank=True,
        help_text="Sug'urta amal qilish muddati",
    )
    tech_inspection_date = models.DateField(
        null=True,
        blank=True,
        help_text="Texnik ko'rik muddati",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.AVAILABLE,
        help_text="Avtomobil holati: available, repairing, not_available",
    )
    instructor = models.ForeignKey(
        "User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={"role": "instructor"},
        related_name="assigned_cars",
        help_text="Ushbu avtomobilga biriktirilgan instruktor",
    )
    mileage = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Probeg (km)",
    )
    oil_change_date = models.DateField(
        null=True,
        blank=True,
        help_text="Moy so'nggi almashtirilgan sana",
    )
    oil_change_mileage = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Moy so'nggi almashtirilgandagi probeg (km). Joriy probeg bilan solishtirib, keyingi almashtirishgacha necha km qolganini hisoblash uchun ishlatiladi.",
    )
    oil_change_interval_km = models.PositiveIntegerField(
        default=5000,
        help_text="Moy almashtirish oralig'i (km). Necha km da moy almashtirilishi kerakligini belgilaydi (standart: 5000 km).",
    )
    last_washed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Oxirgi marta yuvilgan sana va vaqt (avtomatik to'ldiriladi)",
    )

    class Meta:
        db_table = "car"
        verbose_name = "Avtomobil"
        verbose_name_plural = "Avtomobillar"
        ordering = ["car_name"]

    def __str__(self):
        return f"{self.car_name} ({self.status})"


class CarAssignmentHistory(BaseModel):
    """
    Tracks which instructor was assigned to a car and when — a full history
    of assignments, not just the current one on Car.instructor.
    """

    car = models.ForeignKey(
        Car,
        on_delete=models.CASCADE,
        related_name="assignment_history",
    )
    instructor = models.ForeignKey(
        "User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={"role": "instructor"},
        related_name="car_assignment_history",
    )
    assigned_at = models.DateTimeField(default=timezone.now)
    unassigned_at = models.DateTimeField(null=True, blank=True)

    # Snapshot of the car's oil-service state at the moment this instructor
    # was unassigned, so the history row shows what they handed the car over
    # with (rather than the car's current, possibly since-updated, values).
    mileage_at_unassignment = models.PositiveIntegerField(null=True, blank=True)
    oil_change_date_at_unassignment = models.DateField(null=True, blank=True)
    oil_change_mileage_at_unassignment = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        db_table = "car_assignment_history"
        verbose_name = "Avtomobil biriktirish tarixi"
        verbose_name_plural = "Avtomobil biriktirish tarixi"
        ordering = ["-assigned_at"]

    def __str__(self):
        who = self.instructor.full_name if self.instructor else "Noma'lum"
        return f"{self.car.car_name} - {who} ({self.assigned_at:%Y-%m-%d})"


class CarWash(BaseModel):
    """
    A single car-washing record. `washed_at` is always set server-side to the
    current time when the record is created — it is never accepted from the
    client, so instructors cannot backdate a wash.
    """

    car = models.ForeignKey(
        Car,
        on_delete=models.CASCADE,
        related_name="wash_history",
    )
    instructor = models.ForeignKey(
        "User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={"role": "instructor"},
        related_name="car_washes",
    )
    washed_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "car_wash"
        verbose_name = "Avtomobil yuvish tarixi"
        verbose_name_plural = "Avtomobil yuvish tarixi"
        ordering = ["-washed_at"]

    def __str__(self):
        who = self.instructor.full_name if self.instructor else "Noma'lum"
        return f"{self.car.car_name} - {who} ({self.washed_at:%Y-%m-%d %H:%M})"


class DrivingLessons(BaseModel):
    """Driving lesson confirmation model. Also covers autodrome (Avtodrom)
    practice sessions, which are capped at 6 total hours per student."""

    class LessonType(models.TextChoices):
        DRIVING = "driving", "Amaliy haydash"
        AUTODROME = "autodrome", "Avtodrom"

    AUTODROME_MAX_HOURS = 6

    branch = models.ForeignKey(
        "Branch",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="driving_lessons",
    )
    lesson_type = models.CharField(
        max_length=20,
        choices=LessonType.choices,
        default=LessonType.DRIVING,
    )
    hours = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Avtodromda o'tkazilgan soatlar soni (faqat Avtodrom turi uchun, 1-6)",
    )
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={"role": User.Role.STUDENT},
        related_name="driving_lessons",
    )
    instructor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={"role": User.Role.INSTRUCTOR},
        related_name="instructor_lessons",
    )
    car = models.ForeignKey(
        Car,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="driving_lessons",
    )
    lesson_date = models.DateTimeField(
        default=timezone.now,
        help_text="Amaliy dars sanasi va vaqti",
    )

    class Meta:
        db_table = "driving_lessons"
        verbose_name = "Amaliy Haydash Darsi"
        verbose_name_plural = "Amaliy Haydash Darslari"
        ordering = ["-lesson_date", "-created_at"]

    def __str__(self):
        return f"{self.student.full_name} - {self.instructor.full_name} ({self.lesson_date})"


class AutodromeAccessGrant(BaseModel):
    """
    Extra autodrome visit allowance an admin/superuser grants a student once
    they've used up the standard AUTODROME_MAX_HOURS (or their group has
    finished). Grants a number of extra visits/hours, valid only within an
    explicit date range (e.g. "6 more times, for the next week").
    """

    student = models.ForeignKey(
        "User",
        on_delete=models.CASCADE,
        limit_choices_to={"role": "student"},
        related_name="autodrome_grants",
    )
    granted_by = models.ForeignKey(
        "User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="autodrome_grants_given",
    )
    branch = models.ForeignKey(
        "Branch",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="autodrome_grants",
    )
    visits = models.PositiveSmallIntegerField(
        help_text="Necha marta avtodromga qayta borishga ruxsat berilgan",
    )
    start_date = models.DateField(help_text="Amal qilish boshlanish sanasi")
    end_date = models.DateField(help_text="Amal qilish tugash sanasi")

    class Meta:
        db_table = "autodrome_access_grant"
        verbose_name = "Avtodrom qo'shimcha ruxsati"
        verbose_name_plural = "Avtodrom qo'shimcha ruxsatlari"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student.full_name} - {self.visits}x ({self.start_date} - {self.end_date})"


class Notification(BaseModel):
    """System notifications model."""

    class Status(models.TextChoices):
        DRIVING_LESSON = "driving_lesson", "Amaliy Haydash Darsi"
        CERTIFICATE_UPLOAD = "certificate_upload", "Sertifikat Yuklash"
        PAYMENT = "payment", "To'lov"
        AGENT_PAYMENT = "agent_payment", "Agent To'lovi"
        REVIEW = "review", "Sharh"

    branch = models.ForeignKey(
        "Branch",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notifications",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications",
        help_text="Qabul qiluvchi (null bo'lsa adminlar uchun)",
    )
    title = models.CharField(max_length=255, help_text="Bildirishnoma sarlavhasi")
    date = models.DateTimeField(default=timezone.now, help_text="Bildirishnoma sanasi")
    note = models.TextField(blank=True, null=True, help_text="Batafsil izoh")
    is_read = models.BooleanField(default=False, db_index=True, help_text="O'qilganlik holati")
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.DRIVING_LESSON,
    )
    target_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text=(
            "Bog'liq obyekt IDsi — status'ga qarab qayerga ishora qilishini "
            "frontend hal qiladi (driving_lesson/certificate_upload -> "
            "o'quvchi ID, review -> o'qituvchi/instruktor ID)."
        ),
    )

    class Meta:
        db_table = "notification"
        verbose_name = "Bildirishnoma"
        verbose_name_plural = "Bildirishnomalar"
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"{self.title} ({self.status})"


class TeacherReview(BaseModel):
    """A review a student leaves for one of their teachers (coordinator or instructor)."""

    branch = models.ForeignKey(
        "Branch",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="teacher_reviews",
    )
    student = models.ForeignKey(
        "User",
        on_delete=models.CASCADE,
        limit_choices_to={"role": "student"},
        related_name="reviews_given",
        help_text="Sharh qoldirgan o'quvchi",
    )
    teacher = models.ForeignKey(
        "User",
        on_delete=models.CASCADE,
        limit_choices_to={"role__in": ["instructor", "coordinator"]},
        related_name="reviews_received",
        help_text="Sharh qoldirilgan o'qituvchi yoki instruktor",
    )
    rating = models.PositiveSmallIntegerField(
        default=5,
        help_text="Baho (1 dan 5 gacha)",
    )
    comment = models.TextField(
        blank=True,
        null=True,
        help_text="Sharh matni",
    )

    class Meta:
        db_table = "teacher_review"
        verbose_name = "O'qituvchi sharhi"
        verbose_name_plural = "O'qituvchi sharhlari"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student.full_name} -> {self.teacher.full_name} ({self.rating}/5)"


class Attendance(BaseModel):
    """
    Per-day absence mark a teacher (coordinator) or instructor records for one
    of their assigned students. Only today's record is ever writable from the
    client (enforced in the view) — past days are frozen history, future days
    don't exist yet.
    """

    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name="attendance_records",
    )
    date = models.DateField(help_text="Yo'qlama sanasi")
    is_absent = models.BooleanField(
        default=True,
        help_text="Belgilangan bo'lsa, o'quvchi shu kuni darsga kelmagan",
    )
    marked_by = models.ForeignKey(
        "User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="attendance_marks",
        help_text="Yo'qlamani belgilagan o'qituvchi/instruktor",
    )

    class Meta:
        db_table = "attendance"
        verbose_name = "Davomat"
        verbose_name_plural = "Davomatlar"
        ordering = ["-date"]
        unique_together = ["enrollment", "date"]

    def __str__(self):
        state = "Kelmadi" if self.is_absent else "Keldi"
        return f"{self.enrollment.student.full_name} - {self.date} ({state})"


class StudentCertificate(BaseModel):
    """A certificate photo a teacher (coordinator) uploads for a specific student."""

    branch = models.ForeignKey(
        "Branch",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="student_certificates",
    )
    student = models.ForeignKey(
        "User",
        on_delete=models.CASCADE,
        limit_choices_to={"role": "student"},
        related_name="certificates",
        help_text="Sertifikat tegishli bo'lgan o'quvchi",
    )
    coordinator = models.ForeignKey(
        "User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={"role": "coordinator"},
        related_name="uploaded_certificates",
        help_text="Sertifikatni yuklagan o'qituvchi",
    )
    image = models.FileField(
        upload_to="certificates/",
        help_text="Sertifikat rasmi",
    )
    bonus_payment = models.ForeignKey(
        "Payment",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="certificate",
        help_text="Ushbu sertifikat uchun o'qituvchiga to'langan bonus to'lovi (agar to'langan bo'lsa)",
    )

    class Meta:
        db_table = "student_certificate"
        verbose_name = "O'quvchi sertifikati"
        verbose_name_plural = "O'quvchi sertifikatlari"
        ordering = ["-created_at"]

    def __str__(self):
        who = self.instructor.full_name if self.instructor else "Noma'lum"
        return f"{self.student.full_name} - {who}"


