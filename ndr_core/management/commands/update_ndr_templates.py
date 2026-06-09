"""Management command to update app page templates from ndr_core's app_init sources."""
import os
import shutil

from django.contrib.staticfiles import finders
from django.core.management.base import BaseCommand

from ndr_core.ndr_settings import NdrSettings

# HTML files in app_init that are page templates (exclude css, py, txt, png, mmdb)
TEMPLATE_FILES = [
    'base.html',
    'index.html',
    'search.html',
    'data_list.html',
    'viewer.html',
    'fullscreen.html',
    'flip_book.html',
    'about_us.html',
    'contact.html',
    'template.html',
    'test.html',
]


class Command(BaseCommand):
    help = 'Update app page templates from ndr_core app_init sources.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--template',
            type=str,
            default=None,
            help='Update only the named template file (e.g. base.html). Omit to update all.',
        )
        parser.add_argument(
            '--list',
            action='store_true',
            default=False,
            help='List available templates and whether they exist in the app, then exit.',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            default=False,
            help='Skip confirmation prompt.',
        )

    def handle(self, *args, **options):
        templates_dir = NdrSettings.get_templates_path()

        if options['list']:
            self.stdout.write('Available app_init templates:')
            for name in TEMPLATE_FILES:
                dest = os.path.join(templates_dir, name)
                status = self.style.SUCCESS('exists') if os.path.isfile(dest) else self.style.WARNING('missing')
                self.stdout.write(f'  {name:30s} [{status}]')
            return

        # Determine which files to update
        if options['template']:
            target = options['template']
            if target not in TEMPLATE_FILES:
                self.stdout.write(self.style.ERROR(
                    f'Unknown template "{target}". Use --list to see available templates.'
                ))
                return
            targets = [target]
        else:
            targets = TEMPLATE_FILES

        # Resolve sources and destinations
        plan = []
        for name in targets:
            source = finders.find(f'ndr_core/app_init/{name}')
            if source is None:
                self.stdout.write(self.style.WARNING(f'  Source not found for "{name}", skipping.'))
                continue
            dest = os.path.join(templates_dir, name)
            plan.append((name, source, dest))

        if not plan:
            self.stdout.write(self.style.WARNING('Nothing to update.'))
            return

        # Show plan
        self.stdout.write('The following templates will be overwritten:')
        for name, source, dest in plan:
            exists = '(overwrite)' if os.path.isfile(dest) else '(new)'
            self.stdout.write(f'  {name} {exists}')
            self.stdout.write(f'    src : {source}')
            self.stdout.write(f'    dest: {dest}')

        # Confirm unless --force
        if not options['force']:
            confirm = input('\nProceed? (y/n) ')
            if confirm.lower() != 'y':
                self.stdout.write(self.style.ERROR('Aborted.'))
                return

        # Execute
        if not os.path.isdir(templates_dir):
            os.makedirs(templates_dir)

        for name, source, dest in plan:
            shutil.copyfile(source, dest)
            self.stdout.write(self.style.SUCCESS(f'  Copied {name}'))

        self.stdout.write(self.style.SUCCESS('Done.'))
