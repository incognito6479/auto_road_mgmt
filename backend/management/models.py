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
    Roles: superuser, admin, mechanic, instructor, coordinator.
    """

    class Role(models.TextChoices):
        SUPERUSER = "superuser", "Superuser"
        ADMIN = "admin", "Admin"
        MECHANIC = "mechanic", "Mexanik"
        INSTRUCTOR = "instructor", "Instruktor"
        COORDINATOR = "coordinator", "Kordinator"

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

    jshshr = models.BigIntegerField(
        help_text="Namuna: 29572006200016",
    )

    passport_serie = models.CharField(
        max_length=2,
        help_text="Namuna: AB",
    )

    passport_number = models.IntegerField(
        help_text="Namuna: 2275679",
    )

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        db_table = "user"
        verbose_name = "User"
        verbose_name_plural = "Users"
        unique_together = ["phone", "jshshr"]

    def __str__(self):
        return f"{self.phone} ({self.role})"


class Student(BaseModel):
    """Driving school student."""

    full_name = models.CharField(max_length=255)

    phone = models.CharField(
        max_length=20,
        help_text="Namuna: 998909009090",
    )

    jshshr = models.BigIntegerField(
        help_text="Namuna: 29572006200016",
    )

    passport_serie = models.CharField(
        max_length=2,
        help_text="Namuna: AB",
    )

    passport_number = models.IntegerField(
        help_text="Namuna: 2275679",
    )

    class Meta:
        db_table = "student"
        verbose_name = "Student"
        verbose_name_plural = "Students"
        unique_together = ["phone", "jshshr"]

    def __str__(self):
        return self.full_name


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

    class Meta:
        db_table = "category"
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Enrollment(BaseModel):
    """Student enrollment in a driving license category."""

    class Status(models.TextChoices):
        NEW = "new", "Yangi"
        ENROLLED = "enrolled", "Qabul qilingan"
        FINISHED = "finished", "Tugatgan"
        CANCELED = "canceled", "Bekor qilingan"

    student = models.ForeignKey(
        Student,
        on_delete=models.PROTECT,
        related_name="enrollments",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="enrollments",
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
        return f"{self.student.full_name if self.student else 'No Student'} - {self.amount} ({self.status})"
