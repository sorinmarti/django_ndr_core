"""Management command to export an NDR Core project to a portable zip archive."""
import os
import shutil
import tempfile
import zipfile

from django.core.management.base import BaseCommand, CommandError
from ndr_core.ndr_settings import NdrSettings


class Command(BaseCommand):
    help = (
        'Export the NDR Core project (database, media, app) to a zip archive. '
        'Import on the server with: python manage.py import_ndr_project <archive.zip>'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            type=str,
            default='ndr_export.zip',
            metavar='FILE',
            help='Output zip file path (default: ndr_export.zip).',
        )
        parser.add_argument(
            '--no-media',
            action='store_true',
            default=False,
            help='Skip media files.',
        )
        parser.add_argument(
            '--no-app',
            action='store_true',
            default=False,
            help='Skip the ndr app directory (templates, views, urls, css).',
        )

    def handle(self, *args, **options):
        output_path = options['output']
        include_media = not options['no_media']
        include_app = not options['no_app']

        app_name = NdrSettings.APP_NAME  # 'ndr'

        with tempfile.TemporaryDirectory() as tmpdir:

            # 1. SQLite database
            db_path = 'db.sqlite3'
            if not os.path.isfile(db_path):
                raise CommandError(
                    f'db.sqlite3 not found. Only SQLite projects are supported by this command.'
                )
            shutil.copy2(db_path, os.path.join(tmpdir, 'db.sqlite3'))
            self.stdout.write(self.style.SUCCESS('  db.sqlite3'))

            # 2. Media files
            if include_media:
                media_src = 'media'
                if os.path.isdir(media_src):
                    shutil.copytree(media_src, os.path.join(tmpdir, 'media'))
                    self.stdout.write(self.style.SUCCESS('  media/'))
                else:
                    self.stdout.write('  media/ not found, skipping.')

            # 3. The ndr app
            if include_app:
                if os.path.isdir(app_name):
                    def ignore_pycache(src, names):
                        return [n for n in names if n == '__pycache__' or n.endswith('.pyc')]
                    shutil.copytree(app_name, os.path.join(tmpdir, app_name), ignore=ignore_pycache)
                    self.stdout.write(self.style.SUCCESS(f'  {app_name}/'))
                else:
                    self.stdout.write(f'  {app_name}/ not found, skipping.')

            # 4. Bundle into zip
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                for root, dirs, files in os.walk(tmpdir):
                    dirs[:] = [d for d in dirs if d != '__pycache__']
                    for file in files:
                        abs_path = os.path.join(root, file)
                        arc_name = os.path.relpath(abs_path, tmpdir)
                        zf.write(abs_path, arc_name)

        size_mb = os.path.getsize(output_path) / (1024 * 1024)
        self.stdout.write(self.style.SUCCESS(
            f'\nExport complete: {output_path} ({size_mb:.1f} MB)'
        ))
        self.stdout.write(
            f'Import on server: python manage.py import_ndr_project {output_path}'
        )