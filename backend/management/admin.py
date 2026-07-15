from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from management.models import Category, Student, User, Enrollment, Payment


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Columns shown in the list view
    list_display = (
        "id", "phone", "role", "first_name", "last_name", "email",
        "jshshr", "passport_serie", "passport_number",
        "is_staff", "is_superuser", "is_active", "date_joined", "last_login"
    )
    list_filter = ("role", "is_staff", "is_superuser", "is_active")
    search_fields = ("phone", "first_name", "last_name", "jshshr")
    ordering = ("phone",)

    # All fields editable on the change form
    fieldsets = (
        (None, {
            "fields": ("phone", "password"),
        }),
        ("Shaxsiy ma'lumotlar", {
            "fields": (
                "first_name", "last_name", "email",
                "jshshr", "passport_serie", "passport_number",
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

    # All fields editable on the add (create) form
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "phone", "password1", "password2",
                "first_name", "last_name", "email",
                "role", "jshshr", "passport_serie", "passport_number",
                "is_active", "is_staff", "is_superuser",
            ),
        }),
    )


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        "id", "full_name", "phone", "jshshr",
        "passport_serie", "passport_number",
        "is_active", "notes", "created_at", "updated_at"
    )
    list_filter = ("is_active", "created_at")
    search_fields = ("full_name", "phone", "jshshr")
    ordering = ("full_name",)
    readonly_fields = ("id", "created_at", "updated_at")
    fields = (
        "full_name", "phone", "jshshr", "passport_serie",
        "passport_number", "notes", "is_active", "created_at", "updated_at"
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "price", "is_active", "notes", "created_at", "updated_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("name",)
    ordering = ("name",)
    readonly_fields = ("id", "created_at", "updated_at")
    fields = ("name", "price", "notes", "is_active", "created_at", "updated_at")


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("id", "student", "category", "status", "enrolled_free", "enrolled_amount", "is_active", "notes", "created_at", "updated_at")
    list_filter = ("status", "enrolled_free", "is_active", "created_at")
    search_fields = ("student__full_name", "category__name")
    ordering = ("-created_at",)
    readonly_fields = ("id", "created_at", "updated_at")
    fields = ("student", "category", "status", "enrolled_free", "enrolled_amount", "notes", "is_active", "created_at", "updated_at")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "enrollment", "amount", "status", "method", "is_active", "notes", "created_at", "updated_at")
    list_filter = ("status", "method", "is_active", "created_at")
    search_fields = ("enrollment__student__full_name", "user__phone")
    ordering = ("-created_at",)
    readonly_fields = ("id", "created_at", "updated_at")
    fields = ("enrollment", "user", "amount", "status", "method", "notes", "is_active", "created_at", "updated_at")
