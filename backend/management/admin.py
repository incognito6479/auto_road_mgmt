from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from management.models import Category, Student, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Columns shown in the list view
    list_display = (
        "phone", "role", "first_name", "last_name",
        "jshshr", "passport_serie", "passport_number",
        "is_staff", "is_active",
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
    # Columns shown in the list view
    list_display = (
        "full_name", "phone",
        "jshshr", "passport_serie", "passport_number",
        "is_active", "created_at", "updated_at",
    )
    list_filter = ("is_active",)
    search_fields = ("full_name", "phone", "jshshr")
    ordering = ("full_name",)

    # All fields editable on the change / add form
    fieldsets = (
        ("Asosiy ma'lumotlar", {
            "fields": ("full_name", "phone"),
        }),
        ("Hujjat ma'lumotlari", {
            "fields": ("jshshr", "passport_serie", "passport_number"),
        }),
        ("Holat", {
            "fields": ("is_active",),
        }),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "is_active", "created_at", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("name",)
    ordering = ("name",)

    fieldsets = (
        ("Asosiy ma'lumotlar", {
            "fields": ("name", "price"),
        }),
        ("Holat", {
            "fields": ("is_active",),
        }),
    )
