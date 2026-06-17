"""Management command to import an NDR Core project from a zip archive."""
import os
import shutil
import tempfile
import zipfile

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from ndr_core.ndr_settings import NdrSettings


class Command(BaseCommand):
    help = (
        'Import an NDR Core project from a zip archive produced by export_ndr_project. '
        'Restores the database, media files, and the ndr app.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            'archive',
            type=str,
            help='Path to the zip archive created by export_ndr_project.',
        )
        parser.add_argument(
            '--no-media',
            action='store_true',
            default=False,
            help='Skip restoring media files.',
        )
        parser.add_argument(
            '--no-app',
            action='store_true',
            default=False,
            help='Skip restoring the ndr app directory.',
        )

    def handle(self, *args, **options):
        archive_path = options['archive']
        restore_media = not options['no_media']
        restore_app = not options['no_app']

        app_name = NdrSettings.APP_NAME  # 'ndr'

        if not os.path.isfile(archive_path):
            raise CommandError(f'Archive not found: {archive_path}')
        if not zipfile.is_zipfile(archive_path):
            raise CommandError(f'Not a valid zip file: {archive_path}')

        with tempfile.TemporaryDirectory() as tmpdir:
            self.stdout.write(f'Extracting {archive_path}...')
            with zipfile.ZipFile(archive_path, 'r') as zf:
                zf.extractall(tmpdir)

            # 1. SQLite database — replace entirely
            db_src = os.path.join(tmpdir, 'db.sqlite3')
            if os.path.isfile(db_src):
                shutil.copy2(db_src, 'db.sqlite3')
                self.stdout.write(self.style.SUCCESS('  db.sqlite3 restored.'))
            else:
                self.stdout.write(self.style.WARNING('  db.sqlite3 not found in archive.'))

            # 2. Media files — merge (existing files not in the archive are kept)
            if restore_media:
                media_src = os.path.join(tmpdir, 'media')
                if os.path.isdir(media_src):
                    os.makedirs('media', exist_ok=True)
                    for item in os.listdir(media_src):
                        s = os.path.join(media_src, item)
                        d = os.path.join('media', item)
                        if os.path.isdir(s):
                            if os.path.exists(d):
                                shutil.rmtree(d)
                            shutil.copytree(s, d)
                        else:
                            shutil.copy2(s, d)
                    self.stdout.write(self.style.SUCCESS('  media/ restored.'))
                else:
                    self.stdout.write('  No media/ in archive, skipping.')

            # 3. The ndr app — replace entirely
            if restore_app:
                app_src = os.path.join(tmpdir, app_name)
                if os.path.isdir(app_src):
                    if os.path.exists(app_name):
                        shutil.rmtree(app_name)
                    shutil.copytree(app_src, app_name)
                    self.stdout.write(self.style.SUCCESS(f'  {app_name}/ restored.'))
                else:
                    self.stdout.write(f'  No {app_name}/ in archive, skipping.')

        # Run migrate in case the archive has a db from a different migration state
        self.stdout.write('Running migrate...')
        call_command('migrate', verbosity=1)

        self.stdout.write(self.style.SUCCESS('\nImport complete.'))
        self.stdout.write("Run 'python manage.py collectstatic --noinput' to publish static files.")