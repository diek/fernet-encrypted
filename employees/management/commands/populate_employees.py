import csv
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from employees.models import Employee, City, Relationship
from datetime import datetime


class Command(BaseCommand):
    help = "Populate Employee table from employees_employee.csv"

    def add_arguments(self, parser):
        parser.add_argument(
            "csv_file",
            type=str,
            nargs="?",
            default="employees_employee.csv",
            help="Path to the CSV file (default: employees_employee.csv)",
        )

    def handle(self, *args, **options):
        csv_file = options["csv_file"]

        try:
            with open(csv_file, "r", encoding="utf-8-sig") as file:
                reader = csv.DictReader(file)

                # Strip whitespace from headers
                reader.fieldnames = [name.strip() for name in reader.fieldnames]

                created_count = 0
                updated_count = 0
                skipped_count = 0
                error_count = 0

                with transaction.atomic():
                    for row_num, row in enumerate(reader, start=2):
                        # Strip whitespace from all values
                        row = {k: v.strip() if v else v for k, v in row.items()}

                        # Skip if no email present
                        email = row.get("email", "").strip()
                        if not email:
                            self.stdout.write(
                                self.style.WARNING(
                                    f"Row {row_num}: Skipped - no email provided"
                                )
                            )
                            skipped_count += 1
                            continue

                        try:
                            employee_data = self.parse_row(row)

                            # Check if employee exists
                            employee, created = Employee.objects.update_or_create(
                                email=email, defaults=employee_data
                            )

                            if created:
                                created_count += 1
                                self.stdout.write(
                                    self.style.SUCCESS(
                                        f"Row {row_num}: Created employee {email}"
                                    )
                                )
                            else:
                                updated_count += 1
                                self.stdout.write(
                                    self.style.SUCCESS(
                                        f"Row {row_num}: Updated employee {email}"
                                    )
                                )

                        except Exception as e:
                            error_count += 1
                            self.stdout.write(
                                self.style.ERROR(
                                    f"Row {row_num}: Error processing {email}: {str(e)}"
                                )
                            )

                self.stdout.write(self.style.SUCCESS(f"\n=== Summary ==="))
                self.stdout.write(self.style.SUCCESS(f"Created: {created_count}"))
                self.stdout.write(self.style.SUCCESS(f"Updated: {updated_count}"))
                self.stdout.write(self.style.WARNING(f"Skipped: {skipped_count}"))
                self.stdout.write(self.style.ERROR(f"Errors: {error_count}"))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"File not found: {csv_file}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error reading CSV file: {str(e)}"))

    def parse_row(self, row):
        """Parse a CSV row into Employee model fields"""
        data = {}

        # Required fields
        data["email"] = row.get("email", "").strip()
        data["first_name"] = row.get("first_name", "").strip()
        data["last_name"] = row.get("last_name", "").strip()

        # Optional text fields
        data["middle_name"] = row.get("middle_name", "").strip() or None
        data["sin"] = row.get("sin", "").strip()
        data["address"] = row.get("address", "").strip()
        data["address2"] = row.get("address2", "").strip()
        data["postal_code"] = row.get("postal_code", "").strip()
        data["phone_number"] = row.get("phone_number", "").strip()
        data["extra_phone_number"] = row.get("extra_phone_number", "").strip() or None
        data["emergency_phone_number"] = row.get("emergency_phone_number", "").strip()
        data["emergency_contact_name"] = row.get("emergency_contact_name", "").strip()
        data["notes"] = row.get("notes", "").strip() or None
        data["color"] = row.get("color", "").strip() or "AAAAAA"

        # Boolean fields
        is_active = row.get("is_active", "True").strip()
        data["is_active"] = is_active.lower() in ("true", "1", "yes", "t")

        # Date fields
        data["date_of_birth"] = self.parse_date(row.get("date_of_birth"))
        data["date_hired"] = (
            self.parse_date(row.get("date_hired")) or timezone.localdate()
        )
        data["date_released"] = self.parse_date(row.get("date_released")) or None

        # Integer fields
        data["iss_iat_id"] = self.parse_int(row.get("iss_iat_id"))
        data["mss_id"] = self.parse_int(row.get("mss_id"))
        data["iss_security_license_number"] = self.parse_int(
            row.get("iss_security_license_number")
        )
        data["iat_security_license_number"] = self.parse_int(
            row.get("iat_security_license_number")
        )
        data["mss_security_license_number"] = self.parse_int(
            row.get("mss_security_license_number")
        )
        data["weekly_hours"] = self.parse_int(row.get("weekly_hours")) or 0

        # Decimal fields
        data["salary"] = self.parse_decimal(row.get("salary"))

        # Foreign key fields
        city_id = row.get("city_id", "").strip()
        if city_id:
            try:
                data["city_id"] = int(city_id)
            except (ValueError, TypeError):
                data["city_id"] = City.HALIFAX_ID
        else:
            data["city_id"] = City.HALIFAX_ID

        relationship_id = row.get("emergency_relationship_id", "").strip()
        if relationship_id:
            try:
                data["emergency_relationship_id"] = int(relationship_id)
            except (ValueError, TypeError):
                data["emergency_relationship_id"] = None
        else:
            data["emergency_relationship_id"] = None

        return data

    def parse_date(self, date_str):
        """Parse date string in various formats"""
        if not date_str or not date_str.strip():
            return None

        date_str = date_str.strip()
        date_formats = ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d"]

        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue

        raise ValueError(f"Unable to parse date: {date_str}")

    def parse_int(self, value):
        """Parse integer value"""
        if not value or not str(value).strip():
            return None
        try:
            return int(str(value).strip())
        except (ValueError, TypeError):
            return None

    def parse_decimal(self, value):
        """Parse decimal value"""
        if not value or not str(value).strip():
            return None
        try:
            from decimal import Decimal

            return Decimal(str(value).strip())
        except (ValueError, TypeError):
            return None
