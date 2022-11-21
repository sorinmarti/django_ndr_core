import os
import shutil

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.staticfiles import finders

from ndr_core.models import NdrCorePage
from ndr_core.ndr_settings import NdrSettings


class Command(BaseCommand):
    help = 'This command initializes your ndr_core app'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        app_name = NdrSettings.APP_NAME

        if os.path.isdir(app_name):
            self.stdout.write(f'ERROR: directory "{app_name}" already exists.')
            return

        urls_file = finders.find('ndr_core/app_init/urls.py')
        if not os.path.isfile(urls_file):
            self.stdout.write(f'ERROR: static files to copy not found')
            return

        # Create a new app
        call_command('startapp', app_name)
        self.stdout.write(f'Created new app "{app_name}"')
        os.makedirs(f"{app_name}/templates/{app_name}")

        # Load initial settings data
        call_command('loaddata', 'initial_values.json', app_label='ndr_core')
        call_command('loaddata', 'schemas.json', app_label='ndr_core')
        call_command('loaddata', 'base_styles.json', app_label='ndr_core')
        call_command('loaddata', 'color_palettes.json', app_label='ndr_core')

        if User.objects.filter(username='ndr_core_admin').count() == 0:
            User.objects.create_user(username='ndr_core_admin',
                                     password='ndr_core',
                                     is_superuser=True)
            self.stdout.write(f'Created new user "ndr_core_admin"')
        else:
            self.stdout.write(f'Skipped creating new user "ndr_core_admin". Already exists.')

        # Copy urls.py
        shutil.copyfile(urls_file, f'{app_name}/urls.py')

        # html files
        base_file = finders.find('ndr_core/app_init/base.html')
        shutil.copyfile(base_file, f'{app_name}/templates/{app_name}/base.html')

        index_file = finders.find('ndr_core/app_init/index.html')
        shutil.copyfile(index_file, f'{app_name}/templates/{app_name}/index.html')

        test_file = finders.find('ndr_core/app_init/test.html')
        shutil.copyfile(test_file, f'{app_name}/templates/{app_name}/test.html')

        # static files
        os.makedirs(f'{app_name}/static/{app_name}/css/')
        css_file = finders.find('ndr_core/app_init/style.css')
        shutil.copyfile(css_file, f'{app_name}/static/{app_name}/css/style.css')

        # Pages
        NdrCorePage.objects.create(name='Home Page',
                                   label='Home',
                                   view_name='index',
                                   nav_icon='fas-fa home',
                                   index=0)

        self.stdout.write(self.style.SUCCESS('Finished.'))
