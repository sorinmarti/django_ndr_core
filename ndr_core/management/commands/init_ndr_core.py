"""This file holds the init_dr_core management command class."""
import os
import shutil

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.staticfiles import finders
from django.core.management.utils import get_random_secret_key

from ndr_core.models import NdrCorePage, NdrCoreValue
from ndr_core.ndr_settings import NdrSettings


class Command(BaseCommand):
    help = 'This command initializes your ndr_core app.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force-delete-admin-user',
            type=bool,
            default=False,
            help='Indicates if the admin user should be deleted if it exists.'
        )
        parser.add_argument(
            '--admin-user-password',
            type=str,
            default="ndr_core",
            help='Sets the password for the admin user.'
        )
        parser.add_argument(
            '--noinput',
            type=bool,
            default=False,
            help='Skips all user interaction.'
        )

    def print_output(self, message):
        """Prints a message to the console."""
        self.stdout.write(message)

    def print_success(self, message):
        """Prints a success message to the console."""
        self.stdout.write(self.style.SUCCESS(message))

    def print_warn(self, message):
        """Prints a warning message to the console."""
        self.stdout.write(message)

    def print_error(self, message):
        """Prints an error message to the console."""
        self.stdout.write(self.style.ERROR(message))

    def handle(self, *args, **options):
        app_name = NdrSettings.APP_NAME
        user_input = not options['noinput']

        # (1) CHECK IF APP EXISTS
        # Does the app already exist? Delete it or exit
        if os.path.isdir(app_name):
            self.print_error(f'ERROR: directory "{app_name}" already exists.')
            if user_input:
                confirm_command = ''
                while confirm_command != 'y':
                    confirm_command = input(f'Do you want to delete the current installation? (y/n) ')
                    if confirm_command == 'n':
                        self.print_error('Aborted.')
                        return
                call_command('clean_ndr_core')
            else:
                self.print_error('Aborted (app_exists).')
                return

        # If the app does not exist, ask if it should be created, create it, and continue or exit
        else:
            if user_input:
                confirm_command = ''
                while confirm_command != 'y':
                    confirm_command = input(f'Are you sure you want to initialize the NDR Core app? '
                                            f'This is going to create files and directories. (y/n) ')
                    if confirm_command == 'n':
                        self.print_error('Aborted (user_abort).')
                        return
        # (1.5) MIGRATE
        call_command('migrate')

        # (2) CREATE APP
        # Initialize the app
        call_command('startapp', app_name)
        self.print_success(f'Created new app "{app_name}"')

        # (3) INITIALIZE VALUES
        admin_user_password = options['admin_user_password']
        force_delete_admin_user = options['force_delete_admin_user']

        directories_to_create = [
            NdrSettings.get_templates_path(),
            NdrSettings.get_static_path(),
            NdrSettings.get_images_path(),
            NdrSettings.get_css_path(),
        ]

        fixtures_to_load = [
            'initial_values.json',
            'api_implementations.json',
            'base_styles.json',
            'color_palettes.json',
        ]

        files_to_copy = [
            ('urls.py', f'{NdrSettings.APP_NAME}/urls.py'),
            ('base.html', f'{NdrSettings.get_templates_path()}/base.html'),
            ('index.html', f'{NdrSettings.get_templates_path()}/index.html'),
            ('style.css', f'{NdrSettings.get_css_path()}/style.css')]

        media_directories_to_create = [
            'uploads',
            'images']

        # (4) CREATE DIRECTORIES AND FILES
        # Create directories
        self.print_output('>>> Creating directories:')
        for directory in directories_to_create:
            if not os.path.isdir(directory):
                os.makedirs(directory)
                self.print_success(f'>>> Created "{directory}"')
            else:
                self.print_output(f'>>> Skipped "{directory}". Already exists.')

        # Copy files
        self.print_output('>>> Copying files:')
        for file in files_to_copy:
            source_file = finders.find(f'ndr_core/app_init/{file[0]}')
            shutil.copyfile(source_file, file[1])
            self.print_success(f'>>> Copied "{file[0]}" to "{file[1]}"')

        # Create media directories
        self.print_output('Creating media directories...')
        for directory in media_directories_to_create:
            if not os.path.exists(f'media/{directory}/'):
                os.makedirs(f'media/{directory}/')
                self.print_success(f'>>> Created "media/{directory}/"')

        # Create geoip directory
        self.print_output('>>> Creating geoip directory:')
        if not os.path.exists(f'geoip/'):
            os.makedirs(f'geoip/')
            source_file = finders.find(f'ndr_core/app_init/GeoLite2-Country.mmdb')
            shutil.copyfile(source_file, 'geoip/GeoLite2-Country.mmdb')
            self.print_success(f'>>> Created "geoip/"')
        else:
            self.print_output(f'>>> Skipped "geoip/". Already exists.')

        # (5) INITIALIZE VALUES
        # Load fixtures
        self.print_output('>>> Loading fixtures:')
        for fixture in fixtures_to_load:
            call_command('loaddata', fixture, app_label='ndr_core', verbosity=0)
            self.print_success(f'>>> Loaded "{fixture}"')

        # (6) LET THE USER OVERRIDE SOME VALUES
        if user_input:
            values_to_override = [
                'project_title',
                'header_default_title',
                'ndr_language'
            ]
            for value in values_to_override:
                try:
                    value_obj = NdrCoreValue.objects.get(value_name=value)
                    temp_value = input(f'Please enter a value for "{value_obj.value_label} '
                                       f'<default: {value_obj.value_value}>": ')
                    if temp_value != '':
                        value_obj.value_value = temp_value
                        value_obj.save()
                        self.stdout.write(self.style.SUCCESS(f'>>> Updated value "{value}"'))
                except NdrCoreValue.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f'ERROR: Value "{value}" does not exist.'))
        else:
            self.print_warn('>>> Skipped updating values.')

        # (7) CREATE ADMIN USER
        self.print_output('>>> Creating admin user...')
        if force_delete_admin_user:
            User.objects.filter(username='ndr_core_admin').delete()
            self.print_warn('>>> Deleted user "ndr_core_admin"')

        if User.objects.filter(username='ndr_core_admin').count() == 0:
            User.objects.create_user(username='ndr_core_admin',
                                     password=admin_user_password,
                                     is_superuser=True)
            self.print_success('>>> Created new user "ndr_core_admin"')
        else:
            self.print_output('>>> Skipped creating new user "ndr_core_admin". Already exists.')

        # (8) CREATE PAGES
        # Home Page
        NdrCorePage.objects.create(page_type=NdrCorePage.PageType.TEMPLATE,
                                   name='Home Page',
                                   label='Home',
                                   view_name='index',
                                   nav_icon='fas-fa home',
                                   index=0)
        self.print_success('>>> Created new page "Home Page"')

        # (9) UPDATE SETTINGS FILE
        # Copy settings file to create a backup
        self.print_output('>>> Creating backup of settings file...')
        host = "*"
        if user_input:
            host = input(f'Please enter the hostname your installation will be running on. '
                         f'<default: {host}>": ')
        settings_split = os.environ.get("DJANGO_SETTINGS_MODULE").split(".")
        settings_file = os.path.join(os.getcwd(), settings_split[0], f"{settings_split[1]}.py")
        shutil.copyfile(settings_file, f"{settings_file}.bak")

        # Overwrite settings file
        boiler_plate_file = finders.find(f'ndr_core/app_init/settings_boilerplate.txt')
        settings_values = {"PROJECT_NAME": settings_split[0],
                           "SECRET_KEY": get_random_secret_key(),
                           "ALLOWED_HOST": "*",
                           "INITIAL_LANGUAGE_CODE":
                               NdrCoreValue.objects.get(value_name="ndr_language").get_value()}
        with open(boiler_plate_file) as f:
            boiler_plate = f.read()
            for key, value in settings_values.items():
                boiler_plate = boiler_plate.replace("{{" + key + "}}", value)

        if user_input:
            overwrite_settings = input(f'Overwrite settings file "{settings_file}"? (Y/n) ')
        else:
            overwrite_settings = 'y'
        if overwrite_settings == '' or overwrite_settings.lower() == 'y':
            with open(settings_file, "w") as f:
                f.write(boiler_plate)
            self.print_success(f'>>> Updated settings file "{settings_file}"')
        else:
            self.print_warn(f'>>> Skipped. Please update the settings file manually. ')

        # (10) UPDATE PROJECT URLS FILE
        urls_boiler_plate_file = finders.find(f'ndr_core/app_init/project_urls_boilerplate.txt')
        urls_file = os.path.join(os.getcwd(), settings_split[0], "urls.py")
        with open(urls_boiler_plate_file) as f:
            urls_boiler_plate = f.read()
            urls_boiler_plate = urls_boiler_plate.replace("{{PROJECT_NAME}}", settings_split[0])

        if user_input:
            overwrite_urls = input(f'Overwrite urls.py file? (Y/n) ')
        else:
            overwrite_urls = 'y'
        if overwrite_urls == '' or overwrite_settings.lower() == 'y':
            with open(urls_file, "w") as f:
                f.write(urls_boiler_plate)
            self.print_success(f'>>> Updated urls.py file "{urls_file}"')
        else:
            self.print_warn('>>> Skipped. Please update the urls.py file manually. ')
        # (11) FINISH
        self.print_output('Please run "python manage.py collectstatic" to collect static files.')
        self.print_success('Finished.')
