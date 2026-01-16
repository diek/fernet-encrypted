# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Status, Geography, Employee


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(Geography)
class GeographyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'timezone')
    search_fields = ('name',)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'password',
        'last_login',
        'is_superuser',
        'first_name',
        'last_name',
        'is_staff',
        'date_joined',
        'geography',
        'email',
        'middle_name',
        'date_of_birth',
        'sin',
        'sin_e',
        'date_hired',
        'date_released',
        'address',
        'address2',
        'city',
        'postal_code',
        'phone_number',
        'extra_phone_number',
        'status',
        'emergency_phone_number',
        'emergency_contact_name',
        'emergency_relationship',
        'iss_iat_id',
        'mss_id',
        'salary',
        'iss_security_license_number',
        'iat_security_license_number',
        'mss_security_license_number',
        'notes',
        'color',
        'weekly_hours',
    )
    list_filter = (
        'last_login',
        'is_superuser',
        'is_staff',
        'date_joined',
        'date_of_birth',
        'date_hired',
        'date_released',
    )
    raw_id_fields = ('geography', 'city', 'status', 'emergency_relationship')
