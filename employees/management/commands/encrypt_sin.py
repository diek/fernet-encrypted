# employees/management/commands/encrypt_sin.py
from django.core.management.base import BaseCommand
from django.db import transaction

from employees.models import Employee


class Command(BaseCommand):
    help = "Migrate SIN data from sin field to sin_e field"

    def add_arguments(self, parser):
        parser.add_argument(
            "--batch-size",
            type=int,
            default=1000,
            help="Number of records to process in each batch (default: 1000)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Run without making changes to see what would happen",
        )
        parser.add_argument(
            "--force", action="store_true", help="Overwrite existing encrypted values"
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Show detailed output for each record",
        )

    def handle(self, *args, **options):
        batch_size = options["batch_size"]
        dry_run = options["dry_run"]
        force = options["force"]
        verbose = options["verbose"]

        if dry_run:
            self.stdout.write(
                self.style.WARNING("DRY RUN MODE - No changes will be saved")
            )

        # Get statistics first
        total_records = Employee.all_objects.count()
        sin_null = Employee.all_objects.filter(sin__isnull=True).count()
        sin_empty = Employee.all_objects.filter(sin="").count()
        sin_populated = (
            Employee.all_objects.filter(sin__isnull=False).exclude(sin="").count()
        )
        already_encrypted = (
            Employee.all_objects.filter(sin_e__isnull=False).exclude(sin_e="").count()
        )

        self.stdout.write("\n=== Database Statistics ===")
        self.stdout.write(f"Total records: {total_records}")
        self.stdout.write(f"SIN is NULL: {sin_null}")
        self.stdout.write(f"SIN is empty string: {sin_empty}")
        self.stdout.write(f"SIN is populated: {sin_populated}")
        self.stdout.write(f"Already encrypted: {already_encrypted}")
        self.stdout.write("=" * 30 + "\n")

        # Query for records that need migration
        if force:
            queryset = Employee.all_objects.filter(sin__isnull=False).exclude(sin="")
        else:
            # Only migrate records where encrypted field is empty/null
            queryset = Employee.all_objects.filter(sin__isnull=False).exclude(
                sin=""
            ).filter(sin_e__isnull=True) | Employee.all_objects.filter(
                sin__isnull=False
            ).exclude(
                sin=""
            ).filter(
                sin_e=""
            )

        total = queryset.count()
        self.stdout.write(f"Records to migrate: {total}\n")

        if total == 0:
            self.stdout.write(self.style.SUCCESS("No records to migrate"))
            return

        migrated = 0
        skipped = 0
        errors = 0

        # Process in batches
        for obj in queryset.iterator(chunk_size=batch_size):
            # Skip if already encrypted (unless force)
            if not force and obj.sin_e and obj.sin_e != "":
                skipped += 1
                if verbose:
                    self.stdout.write(f"Skipped ID {obj.pk}: already encrypted")
                continue

            if verbose:
                self.stdout.write(
                    f'Processing ID {obj.pk}: sin="{obj.sin}" (len={len(obj.sin)})'
                )

            if not dry_run:
                try:
                    with transaction.atomic():
                        obj.sin_e = obj.sin
                        obj.save(update_fields=["sin_e"])
                    migrated += 1

                    if verbose:
                        # Refresh to see encrypted value
                        obj.refresh_from_db()
                        self.stdout.write(
                            self.style.SUCCESS(f"  ✓ Migrated ID {obj.pk}")
                        )
                except Exception as e:
                    errors += 1
                    self.stdout.write(
                        self.style.ERROR(f"  ✗ Error migrating ID {obj.pk}: {str(e)}")
                    )
            else:
                migrated += 1

            # Progress update every batch
            if (migrated + skipped) % batch_size == 0:
                self.stdout.write(
                    f"Progress: {migrated + skipped}/{total} records processed"
                )

        # Summary
        self.stdout.write("\n" + "=" * 30)
        self.stdout.write(self.style.SUCCESS("Migration complete!"))
        self.stdout.write(f"Migrated: {migrated}")
        self.stdout.write(f"Skipped: {skipped}")
        self.stdout.write(f"Errors: {errors}")
        self.stdout.write("=" * 30)

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "\nThis was a dry run. Run without --dry-run to apply changes."
                )
            )
