from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from management.models import Branch, Category, User, Enrollment, Payment, Group, LearningPlace, Agent, Holidays, Car, DrivingLessons, Notification


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "is_active", "notes", "created_at", "updated_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("name", "notes")
    ordering = ("name",)
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "id", "full_name", "phone", "phone2", "role", "branch", "first_name", "last_name", "email",
        "image", "pass_img", "jshshr", "passport_serie", "passport_number", "notes",
        "is_staff", "is_superuser", "is_active", "date_joined", "last_login"
    )
    list_filter = ("branch", "role", "is_staff", "is_superuser", "is_active")
    search_fields = ("full_name", "phone", "phone2", "first_name", "last_name", "jshshr", "notes")
    ordering = ("phone",)

    fieldsets = (
        (None, {
            "fields": ("phone", "phone2", "password"),
        }),
        ("Shaxsiy ma'lumotlar", {
            "fields": (
                "full_name", "first_name", "last_name", "email", "image", "pass_img", "branch",
                "jshshr", "passport_serie", "passport_number", "notes",
            ),
        }),
        ("Rol va ruxsatlar", {
            "fields": (
                "role", "is_active", "is_staff", "is_superuser",
                "groups", "user_permissions",
            ),
        }),
        ("Oxirgi kirish", {
            "fields": ("last_login", "date_joined"),
        }),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "phone", "phone2", "password1", "password2",
                "full_name", "first_name", "last_name", "email", "image", "pass_img", "branch",
                "role", "jshshr", "passport_serie", "passport_number", "notes",
                "is_active", "is_staff", "is_superuser",
            ),
        }),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "price", "duration", "branch", "is_active", "notes", "created_at", "updated_at")
    list_filter = ("branch", "is_active", "created_at")
    search_fields = ("name",)
    ordering = ("name",)
    readonly_fields = ("id", "created_at", "updated_at")
    fields = ("name", "price", "duration", "branch", "notes", "is_active", "created_at", "updated_at")


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category", "branch", "started_at", "duration", "status", "is_active", "notes", "created_at", "updated_at")
    list_filter = ("branch", "status", "category", "is_active", "started_at")
    search_fields = ("name", "category__name")
    ordering = ("-created_at",)
    readonly_fields = ("id", "created_at", "updated_at")
    fields = ("name", "category", "branch", "started_at", "duration", "status", "notes", "is_active", "created_at", "updated_at")


@admin.register(LearningPlace)
class LearningPlaceAdmin(admin.ModelAdmin):
    list_display = ("id", "place_name", "branch", "is_active", "created_at", "updated_at")
    list_filter = ("branch", "is_active", "created_at")
    search_fields = ("place_name",)
    ordering = ("place_name",)
    readonly_fields = ("id", "created_at", "updated_at")
    fields = ("place_name", "branch", "is_active", "created_at", "updated_at")


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "phone", "phone2", "branch", "is_active", "notes", "created_at", "updated_at")
    list_filter = ("branch", "is_active", "created_at")
    search_fields = ("full_name", "phone", "phone2", "notes")
    ordering = ("full_name",)
    readonly_fields = ("id", "created_at", "updated_at")
    fields = ("full_name", "phone", "phone2", "branch", "notes", "is_active", "created_at", "updated_at")


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = (
        "id", "student", "category", "group", "branch", "instructor", "coordinator", "agent",
        "learning_place", "learning_time", "learning_days",
        "status", "enrolled_free", "enrolled_amount", "is_active", "notes", "created_at", "updated_at"
    )
    list_filter = ("branch", "status", "learning_days", "learning_place", "agent", "enrolled_free", "is_active", "created_at", "group")
    search_fields = ("student__first_name", "student__last_name", "student__phone", "agent__full_name", "agent__phone", "category__name", "group__name", "learning_time")
    ordering = ("-created_at",)
    readonly_fields = ("id", "created_at", "updated_at")
    fields = (
        "student", "category", "group", "branch", "instructor", "coordinator", "agent",
        "learning_place", "learning_time", "learning_days",
        "status", "enrolled_free", "enrolled_amount", "notes", "is_active", "created_at", "updated_at"
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "enrollment", "branch", "amount", "status", "method", "is_active", "notes", "created_at", "updated_at")
    list_filter = ("branch", "status", "method", "is_active", "created_at")
    search_fields = ("enrollment__student__first_name", "enrollment__student__last_name", "user__phone")
    ordering = ("-created_at",)
    readonly_fields = ("id", "created_at", "updated_at")
    fields = ("enrollment", "user", "branch", "amount", "status", "method", "notes", "is_active", "created_at", "updated_at")


@admin.register(Holidays)
class HolidaysAdmin(admin.ModelAdmin):
    list_display = ("id", "holiday_name", "start_date", "end_date", "is_active", "note", "created_at", "updated_at")
    list_filter = ("is_active", "start_date", "end_date")
    search_fields = ("holiday_name", "note")
    ordering = ("-start_date",)
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ("id", "car_name", "image", "status", "manufact_year", "policy_date", "tech_inspection_date", "is_active", "notes", "created_at", "updated_at")
    list_filter = ("status", "manufact_year", "is_active")
    search_fields = ("car_name", "notes")
    ordering = ("car_name",)
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(DrivingLessons)
class DrivingLessonsAdmin(admin.ModelAdmin):
    list_display = ("id", "student", "instructor", "car", "branch", "lesson_date", "is_active", "notes", "created_at", "updated_at")
    list_filter = ("branch", "lesson_date", "is_active")
    search_fields = ("student__full_name", "instructor__full_name", "car__car_name", "notes")
    ordering = ("-lesson_date", "-created_at")
    readonly_fields = ("id", "created_at", "updated_at")
    fields = ("student", "instructor", "car", "branch", "lesson_date", "notes", "is_active", "created_at", "updated_at")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "status", "user", "branch", "is_read", "date", "is_active", "created_at", "updated_at")
    list_filter = ("branch", "status", "is_read", "is_active", "date")
    search_fields = ("title", "note")
    ordering = ("-date", "-created_at")
    readonly_fields = ("id", "created_at", "updated_at")
    fields = ("title", "status", "user", "branch", "is_read", "date", "note", "is_active", "created_at", "updated_at")
