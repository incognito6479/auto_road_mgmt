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
        max_length=20,
        blank=True,
        null=True,
        help_text="Qo'shimcha telefon raqami (namuna: 998909009090)",
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
    working_days = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Ish kunlari soni (kategoriyadan olinadi)",
    )
    working_weekends = models.CharField(
        max_length=20,
        choices=WorkingWeekends.choices,
        default=WorkingWeekends.MWF,
        help_text="Dars kunlari jadvali",
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

    place_name = models.CharField(max_length=255, help_text="O'quv joyi nomi")

    class Meta:
        db_table = "learning_place"
        verbose_name = "Learning Place"
        verbose_name_plural = "Learning Places"

    def __str__(self):
        return self.place_name


class Agent(BaseModel):
    """Agent model for student recruiters/referrals."""

    full_name = models.CharField(max_length=255, help_text="Agent F.I.SH.")
    phone = models.CharField(max_length=20, unique=True, help_text="Telefon raqami")
    phone2 = models.CharField(max_length=20, blank=True, null=True, help_text="Qo'shimcha telefon raqami")

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
        ENROLLED = "enrolled", "Qabul qilingan"
        FINISHED = "finished", "Tugatgan"
        CANCELED = "canceled", "Bekor qilingan"

    class LearningDays(models.TextChoices):
        MWF = "Mo-Wed-Fri", "Mo-Wed-Fri"
        TTS = "Tue-Thu-Sat", "Tue-Thu-Sat"
        EVERYDAY = "everyday", "Everyday"

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
    learning_days = models.CharField(
        max_length=20,
        choices=LearningDays.choices,
        null=True,
        blank=True,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ENROLLED,
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

    class Method(models.TextChoices):
        CASH = "cash", "Naqd"
        CARD = "card", "Karta"
        QR_CODE = "qr_code", "QR code"
        TRANSFER = "transfer", "O'tkazma"

    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="payments",
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

    class Meta:
        db_table = "payment"
        verbose_name = "To'lov"
        verbose_name_plural = "To'lovlar"

    def __str__(self):
        student_name = self.enrollment.student.full_name if (self.enrollment and self.enrollment.student) else 'No Student'
        return f"{student_name} - {self.amount} ({self.status})"
