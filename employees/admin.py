# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Status, Geography, Employee


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Geography)
class GeographyAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "timezone")
    search_fields = ("name",)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    # Minimal list display - just what you need to identify and browse employees
    list_display = (
        "email",
        "first_name",
        "last_name",
        "status",
        "date_hired",
        "is_active",
    )

    list_filter = (
        "status",
        "geography",
        "is_staff",
        "is_superuser",
        "date_hired",
    )

    search_fields = (
        "first_name",
        "last_name",
        "email",
        "sin",
        "phone_number",
    )

    # Organize fields into logical sections in the detail view
    fieldsets = (
        (
            "Personal Information",
            {
                "fields": (
                    "first_name",
                    "middle_name",
                    "last_name",
                    "date_of_birth",
                    "email",
                )
            },
        ),
        (
            "Contact Information",
            {
                "fields": (
                    "phone_number",
                    "extra_phone_number",
                    "address",
                    "address2",
                    "city",
                    "postal_code",
                    "geography",
                )
            },
        ),
        (
            "Emergency Contact",
            {
                "fields": (
                    "emergency_contact_name",
                    "emergency_relationship",
                    "emergency_phone_number",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Employment Information",
            {
                "fields": (
                    "status",
                    "date_hired",
                    "date_released",
                    "salary",
                    "weekly_hours",
                )
            },
        ),
        (
            "Tax & Identification",
            {
                "fields": (
                    "sin",
                    "sin_e",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Security Licenses",
            {
                "fields": (
                    "iss_iat_id",
                    "mss_id",
                    "iss_security_license_number",
                    "iat_security_license_number",
                    "mss_security_license_number",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "System Information",
            {
                "fields": (
                    "is_staff",
                    "is_superuser",
                    "last_login",
                    "date_joined",
                    "password",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Additional Information",
            {
                "fields": (
                    "color",
                    "notes",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    raw_id_fields = ("geography", "city", "status", "emergency_relationship")

    ordering = ("-date_hired",)
