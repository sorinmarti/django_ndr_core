import os
import shutil

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.staticfiles import finders

from ndr_core.models import NdrCorePage, NdrCoreApiConfiguration, NdrCoreApiImplementation
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

        # Create a new app
        call_command('startapp', app_name)
        self.stdout.write(f'Created new app "{app_name}"')
        os.makedirs(f"{app_name}/templates/{app_name}")

        # Load initial settings data
        call_command('loaddata', 'initial_values.json', app_label='ndr_core')
        call_command('loaddata', 'api_implementations.json', app_label='ndr_core')
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
        urls_file = finders.find('ndr_core/app_init/urls.py')
        shutil.copyfile(urls_file, f'{app_name}/urls.py')

        # html files
        base_file = finders.find('ndr_core/app_init/base.html')
        shutil.copyfile(base_file, f'{NdrSettings.get_templates_path()}/base.html')

        index_file = finders.find('ndr_core/app_init/index.html')
        shutil.copyfile(index_file, f'{NdrSettings.get_templates_path()}/index.html')

        search_file = finders.find('ndr_core/app_init/search.html')
        shutil.copyfile(search_file, f'{NdrSettings.get_templates_path()}/search.html')

        test_file = finders.find('ndr_core/app_init/test.html')
        shutil.copyfile(test_file, f'{NdrSettings.get_templates_path()}/test.html')

        # static files
        os.makedirs(f'{NdrSettings.get_css_path()}/')
        css_file = finders.find('ndr_core/app_init/style.css')
        shutil.copyfile(css_file, f'{NdrSettings.get_css_path()}/style.css')

        os.makedirs(f'{NdrSettings.get_images_path()}/')
        logo_file = finders.find('ndr_core/app_init/logo.png')
        shutil.copyfile(logo_file, f'{NdrSettings.get_static_path()}/images/logo.png')

        os.makedirs(f'{NdrSettings.get_sample_data_path()}/')

        # media directory TODO
        if not os.path.exists('media/backgrounds/'):
            os.makedirs('media/backgrounds/')
        if not os.path.exists('media/teams/'):
            os.makedirs('media/teams/')
        if not os.path.exists('media/backgrounds/'):
            os.makedirs('media/backgrounds/')

        # Home Page
        NdrCorePage.objects.create(page_type=NdrCorePage.PageType.TEMPLATE,
                                   name='Home Page',
                                   label='Home',
                                   view_name='index',
                                   nav_icon='fas-fa home',
                                   index=0)

        # Test Search
        api_conf = NdrCoreApiConfiguration.objects.create(api_name='test_api',
                                                          api_host='localhost',
                                                          api_type=NdrCoreApiImplementation.objects.get(name='ndr_core'),
                                                          api_protocol=NdrCoreApiConfiguration.Protocol.HTTP,
                                                          api_port=8000,
                                                          api_label='Local Test API',
                                                          api_description='This configuration queries your local '
                                                                          'installation for test results.',
                                                          api_page_size=10,
                                                          api_url_stub='ndr_core')

        NdrCorePage.objects.create(page_type=NdrCorePage.PageType.SIMPLE_SEARCH,
                                   name='Test Search',
                                   label='Test Search',
                                   view_name='search',
                                   nav_icon='fas-fa search',
                                   index=1,
                                   simple_api=api_conf)

        self.stdout.write(self.style.SUCCESS('Finished.'))
