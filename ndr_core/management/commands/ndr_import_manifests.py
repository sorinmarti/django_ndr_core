"""Management command to import IIIF manifests into NdrCoreManifest."""
import json
import os
import shutil

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from ndr_core.models import NdrCoreManifest, NdrCoreManifestGroup


def _extract_metadata_value(metadata, label):
    """Return the value for the first metadata entry whose label matches (case-insensitive)."""
    if not isinstance(metadata, list):
        return None
    for entry in metadata:
        if isinstance(entry, dict) and str(entry.get('label', '')).strip().lower() == label.lower():
            return str(entry.get('value', '')).strip() or None
    return None


class Command(BaseCommand):
    help = 'Import IIIF v2 manifests from a directory into a manifest group.'

    def add_arguments(self, parser):
        parser.add_argument(
            'directory',
            type=str,
            help='Directory containing the manifest JSON files.',
        )
        parser.add_argument(
            '--group',
            type=int,
            required=True,
            metavar='GROUP_ID',
            help='ID of the NdrCoreManifestGroup to import into.',
        )
        parser.add_argument(
            '--order-field',
            type=str,
            default='Jahr',
            metavar='LABEL',
            help='Metadata label to use for order_value_1 (default: "Jahr").',
        )
        parser.add_argument(
            '--order-field-2',
            type=str,
            default=None,
            metavar='LABEL',
            help='Metadata label to use for order_value_2 (optional).',
        )
        parser.add_argument(
            '--order-field-3',
            type=str,
            default=None,
            metavar='LABEL',
            help='Metadata label to use for order_value_3 (optional).',
        )
        parser.add_argument(
            '--update',
            action='store_true',
            default=False,
            help='Update existing records instead of skipping them.',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            default=False,
            help='Parse and report without writing to the database or copying files.',
        )
        parser.add_argument(
            '--no-copy',
            action='store_true',
            default=False,
            help='Do not copy files to the media directory; store source path as-is.',
        )

    def handle(self, *args, **options):
        directory = options['directory']
        group_id = options['group']
        order_field = options['order_field']
        order_field_2 = options['order_field_2']
        order_field_3 = options['order_field_3']
        do_update = options['update']
        dry_run = options['dry_run']
        no_copy = options['no_copy']

        # Validate directory
        if not os.path.isdir(directory):
            raise CommandError(f"Directory does not exist: {directory}")

        # Validate group
        try:
            group = NdrCoreManifestGroup.objects.get(pk=group_id)
        except NdrCoreManifestGroup.DoesNotExist:
            raise CommandError(
                f"NdrCoreManifestGroup with id={group_id} does not exist. "
                f"Available groups: {list(NdrCoreManifestGroup.objects.values_list('pk', 'title'))}"
            )

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN — no changes will be made."))

        # Prepare media destination
        dest_dir = os.path.join(settings.MEDIA_ROOT, 'uploads', 'manifests')
        if not dry_run and not no_copy:
            os.makedirs(dest_dir, exist_ok=True)

        # Collect all JSON files, sorted by filename for deterministic order
        filenames = sorted(f for f in os.listdir(directory) if f.lower().endswith('.json'))
        total = len(filenames)
        self.stdout.write(f"Found {total} manifest files in '{directory}'.")
        self.stdout.write(f"Importing into group: {group} (id={group_id})")

        created = skipped = updated = errors = 0

        for filename in filenames:
            src_path = os.path.join(directory, filename)
            identifier = os.path.splitext(filename)[0]

            try:
                with open(src_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except (json.JSONDecodeError, OSError) as exc:
                self.stderr.write(self.style.ERROR(f"  ERROR reading {filename}: {exc}"))
                errors += 1
                continue

            # Extract fields from IIIF v2 manifest
            title = str(data.get('label') or '').strip()[:200]
            metadata = data.get('metadata', [])
            ov1 = _extract_metadata_value(metadata, order_field) if order_field else None
            ov2 = _extract_metadata_value(metadata, order_field_2) if order_field_2 else None
            ov3 = _extract_metadata_value(metadata, order_field_3) if order_field_3 else None

            # Determine file path to store
            if no_copy:
                file_path = src_path
            else:
                file_path = f"uploads/manifests/{filename}"

            # Check for existing record
            existing = NdrCoreManifest.objects.filter(identifier=identifier).first()

            if existing:
                if do_update:
                    if not dry_run:
                        existing.title = title
                        existing.manifest_group = group
                        existing.order_value_1 = ov1
                        existing.order_value_2 = ov2
                        existing.order_value_3 = ov3
                        existing.file = file_path
                        existing.save()
                        if not no_copy:
                            shutil.copy2(src_path, os.path.join(dest_dir, filename))
                    self.stdout.write(f"  UPDATED  {identifier}: {title}")
                    updated += 1
                else:
                    self.stdout.write(f"  SKIPPED  {identifier} (already exists)")
                    skipped += 1
                continue

            # Create new record
            if not dry_run:
                NdrCoreManifest.objects.create(
                    identifier=identifier,
                    title=title,
                    file=file_path,
                    manifest_group=group,
                    order_value_1=ov1,
                    order_value_2=ov2,
                    order_value_3=ov3,
                )
                if not no_copy:
                    shutil.copy2(src_path, os.path.join(dest_dir, filename))
            self.stdout.write(self.style.SUCCESS(f"  CREATED  {identifier}: {title}"))
            created += 1

        # Summary
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(f"Done. Created: {created}  Updated: {updated}  Skipped: {skipped}  Errors: {errors}  Total: {total}"))
        if dry_run:
            self.stdout.write(self.style.WARNING("(dry run — nothing was written)"))