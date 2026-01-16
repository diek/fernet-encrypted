from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import EmployeeCreationForm, EmployeeChangeForm
from .models import Status, Employee


class ActiveEmployeeFilter(admin.SimpleListFilter):
    title = "Active employee"
    parameter_name = "active_employee"

    def lookups(self, request, model_admin):
        return (
            ("yes", "Active"),
            ("no", "Inactive"),
        )

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(status_id__in=Status.ACTIVE_IDS)
        if self.value() == "no":
            return queryset.exclude(status_id__in=Status.ACTIVE_IDS)
        return queryset


class EmployeeAdmin(UserAdmin):
    add_form = EmployeeCreationForm
    form = EmployeeChangeForm
    model = Employee
    list_display = (
        "email",
        "is_staff",
        "is_active",
    )
    list_filter = (
        "email",
        "is_staff",
        ActiveEmployeeFilter,
    )
    fieldsets = (
        (None, {"fields": ("email", "is_active", "password")}),
        (
            "Permissions",
            {"fields": ("is_staff", "groups", "user_permissions")},
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
    )
    search_fields = ("email",)
    ordering = ("email",)


admin.site.register(Employee, EmployeeAdmin)
