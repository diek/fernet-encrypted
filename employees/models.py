from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.db.models import Manager
from django.utils import timezone

from encrypted_fields.fields import EncryptedCharField


from misc.models import City, Relationship
from utils.helpers import friendly_capitalize, next_id
from randomcolor import RandomColor

from .managers import CustomUserManager

DEFAULT_COLOR = "c4dce8"

DEFAULT_GEOGRAPHY_NAME = "NS"


class Status(models.Model):
    FULLTIME_ID = 1
    PARTTIME_ID = 2
    CASUAL_ID = 3
    INACTIVE_ID = 4
    ACTIVE_IDS = (FULLTIME_ID, PARTTIME_ID, CASUAL_ID)

    name = models.CharField(max_length=32, unique=True)

    class Meta:
        ordering = ["id"]
        verbose_name_plural = "status"

    def __str__(self):
        return self.name


class Geography(models.Model):
    """
    Area in which a company operates.
    """

    name = models.CharField(
        verbose_name="name",
        max_length=100,
        unique=True,
    )
    timezone = models.CharField(
        verbose_name="time zone",
        max_length=100,
    )

    class Meta:
        verbose_name = "geography"
        verbose_name_plural = "geographies"

    def __str__(self):
        return self.name


class Geographical(models.Model):
    """
    Mixin to associate objects to a geography.
    """

    geography = models.ForeignKey(
        to=Geography,
        on_delete=models.PROTECT,
        related_name="+",
        verbose_name="geography",
    )

    class Meta:
        abstract = True


class Employee(Geographical, AbstractUser):
    username = None
    email = models.EmailField(_("email address"), unique=True)
    middle_name = models.CharField(max_length=32, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    sin = models.CharField("SIN", max_length=11, blank=True)
    sin_e = EncryptedCharField("SIN(e)", max_length=120, null=True)
    date_hired = models.DateField(default=timezone.localdate, null=True, blank=True)
    date_released = models.DateField(null=True, blank=True)

    address = models.CharField("Address line 1", max_length=128, null=True, blank=True)
    address2 = models.CharField("Address line 2", max_length=128, null=True, blank=True)
    city = models.ForeignKey(City, models.PROTECT, default=City.HALIFAX_ID)
    postal_code = models.CharField(max_length=7, null=True, blank=True)
    phone_number = models.CharField(max_length=12, null=True, blank=True)
    extra_phone_number = models.CharField(max_length=12, null=True, blank=True)
    status = models.ForeignKey(Status, models.PROTECT, default=Status.FULLTIME_ID)
    emergency_phone_number = models.CharField(max_length=12, null=True, blank=True)
    emergency_contact_name = models.CharField(max_length=64, null=True, blank=True)
    emergency_relationship = models.ForeignKey(
        Relationship, models.PROTECT, verbose_name="Relationship", null=True, blank=True
    )

    iss_iat_id = models.PositiveIntegerField(
        "ISS/IAT ID", unique=True, null=True, blank=True
    )
    mss_id = models.PositiveIntegerField("MSS ID", unique=True, null=True, blank=True)
    salary = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    iss_security_license_number = models.PositiveIntegerField(
        "ISS Security License Number", null=True, blank=True
    )
    iat_security_license_number = models.PositiveIntegerField(
        "IAT Security License Number", null=True, blank=True
    )
    mss_security_license_number = models.PositiveIntegerField(
        "MSS Security License Number", null=True, blank=True
    )

    notes = models.TextField(null=True, blank=True)

    color = models.CharField(max_length=6, default=DEFAULT_COLOR)
    weekly_hours = models.PositiveSmallIntegerField(
        default=0, help_text="The number of hours this employee works per week"
    )
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = CustomUserManager()
    all_objects = Manager()

    def __str__(self):
        return self.full_name()

    def clean(self):
        if self.status_id in Status.ACTIVE_IDS and self.date_released:
            raise ValidationError("Active employees cannot have a release date.")

        if self.status_id not in Status.ACTIVE_IDS and not self.date_released:
            raise ValidationError("Inactive employees must have a release date.")

        self.address = friendly_capitalize(self.address)

    def save(self, *args, **kwargs):
        if self.color == DEFAULT_COLOR:
            self.color = RandomColor().generate(luminosity="light")[0].lstrip("#")

        # Employees with a release date should be set to inactive.
        if self.date_released is not None:
            self.status_id = Status.INACTIVE_ID

        if self.geography_id is None:
            self.geography = Geography.objects.get(
                name=DEFAULT_GEOGRAPHY_NAME,
            )

        super().save(*args, **kwargs)

    def full_name(self):
        return "%s, %s" % (self.first_name, self.last_name)

    full_name.short_description = "name"
    full_name.admin_order_field = "surname"

    def full_address(self):
        return "%s, %s, %s" % (
            self.address,
            self.city.name,
            self.city.province.abbreviation,
        )

    full_address.short_description = "address"
    full_address.admin_order_field = "address"

    def is_active(self):
        # An employee is considered active if they are full time, part time, or casual
        return self.status_id in Status.ACTIVE_IDS

    is_active.short_description = "active"
    is_active.admin_order_field = "status"
    is_active.boolean = True

    def admin_iss_iat_id(self):
        return self.iss_iat_id or ""

    admin_iss_iat_id.short_description = "ISS/IAT ID"
    admin_iss_iat_id.admin_order_field = "iss_iat_id"

    def admin_mss_id(self):
        return self.mss_id or ""

    admin_mss_id.short_description = "MSS ID"
    admin_mss_id.admin_order_field = "mss_id"

    @staticmethod
    def next_iss_iat_id():
        return next_id(Employee, "iss_iat_id")

    @staticmethod
    def next_mss_id():
        return next_id(Employee, "mss_id")
