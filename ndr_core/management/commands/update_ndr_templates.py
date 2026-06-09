"""Management command to update project page templates from ndr_core app_init sources."""
import filecmp
import os

import shutil

from django.contrib.staticfiles import finders
from django.core.management.base import BaseCommand

from ndr_core.admin_views.page_views import get_base_file_name
from ndr_core.models import NdrCorePage
from ndr_core.ndr_settings import NdrSettings


def get_dest_path(page):
    """Returns the absolute path of the page's template file in the project."""
    return os.path.join(
        NdrSettings.get_templates_path(),
        f'{page.get_full_path()}.html'
    )


class Command(BaseCommand):
    help = 'Check and update project page templates against ndr_core app_init sources.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--list',
            action='store_true',
            default=False,
            help='Show status of all page templates and exit.',
        )
        parser.add_argument(
            '--page',
            type=str,
            default=None,
            metavar='VIEW_NAME',
            help='Update only the page with this view_name (non-interactive).',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            default=False,
            help='Update all outdated templates without prompting.',
        )

    def handle(self, *args, **options):
        pages = NdrCorePage.objects.all().order_by('view_name')

        if not pages.exists():
            self.stdout.write(self.style.WARNING('No pages found in the database.'))
            return

        # Build status table: (page, source_path, dest_path, status)
        rows = []
        for page in pages:
            try:
                source = get_base_file_name(page.page_type)
            except FileNotFoundError:
                source = None

            dest = get_dest_path(page)

            if source is None:
                status = 'no-source'
            elif not os.path.isfile(dest):
                status = 'missing'
            elif filecmp.cmp(source, dest, shallow=False):
                status = 'up-to-date'
            else:
                status = 'differs'

            rows.append((page, source, dest, status))

        # -- LIST mode --
        if options['list']:
            self.stdout.write(f'\n{"Page (view_name)":<35} {"Type":<15} {"Status"}')
            self.stdout.write('-' * 70)
            for page, source, dest, status in rows:
                type_label = page.get_page_type_display()
                if status == 'up-to-date':
                    styled = self.style.SUCCESS(status)
                elif status == 'differs':
                    styled = self.style.WARNING(status)
                elif status == 'missing':
                    styled = self.style.ERROR(status)
                else:
                    styled = status
                self.stdout.write(f'{page.get_full_path():<35} {type_label:<15} {styled}')
            self.stdout.write('')
            return

        # -- SINGLE PAGE mode --
        if options['page']:
            target = options['page']
            match = [(p, s, d, st) for p, s, d, st in rows if p.view_name == target]
            if not match:
                self.stdout.write(self.style.ERROR(f'No page with view_name "{target}" found.'))
                return
            rows = match

        # -- UPDATE mode --
        outdated = [(p, s, d, st) for p, s, d, st in rows if st in ('differs', 'missing')]

        if not outdated:
            self.stdout.write(self.style.SUCCESS('All page templates are up-to-date.'))
            return

        for page, source, dest, status in outdated:
            label = page.get_full_path()
            type_label = page.get_page_type_display()
            self.stdout.write(f'\n  Page : {label}  ({type_label})')
            self.stdout.write(f'  File : {dest}')
            self.stdout.write(f'  Status: {status}')

            if options['force']:
                do_update = True
            else:
                answer = input('  Update this template? (y/n/q) ').strip().lower()
                if answer == 'q':
                    self.stdout.write('Aborted.')
                    return
                do_update = (answer == 'y')

            if do_update:
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                shutil.copyfile(source, dest)
                self.stdout.write(self.style.SUCCESS(f'  Updated.'))
            else:
                self.stdout.write(f'  Skipped.')

        self.stdout.write(self.style.SUCCESS('\nDone.'))
