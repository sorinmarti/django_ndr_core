import os
import shutil

from django.core.management.base import BaseCommand

from ndr_core.models import NdrCoreApiConfiguration, NdrCoreSearchConfiguration, NdrCoreSearchFieldFormConfiguration, \
    NdrCoreCorrectedField, NdrCoreCorrection, NdrCoreColorScheme, NdrCoreUiStyle, NdrCoreValue, NdrCorePage, \
    NdrCoreDataSchema, NdrCoreSearchField, NdrCoreFilterableListConfiguration, NdrCoreApiImplementation
from ndr_core.ndr_settings import NdrSettings


class Command(BaseCommand):
    help = 'Cleans generated ndr_core app with all its assets. This will break your ndr_core installation.'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        app_name = NdrSettings.APP_NAME

        confirmation_input = input(f'Do you really want to delete your ndr_core app?\n '
                                   f'Your ndr_core installation will be reset! Please confirm by typing YES_DELETE: ')

        if confirmation_input == "YES_DELETE":
            if os.path.isdir(app_name):
                shutil.rmtree(app_name, ignore_errors=False, onerror=None)
            if os.path.isdir('media/backgrounds'):
                shutil.rmtree('media/backgrounds', ignore_errors=False, onerror=None)
            if os.path.isdir('media/teams'):
                shutil.rmtree('media/teams', ignore_errors=False, onerror=None)
            if os.path.isdir('media/uploads'):
                shutil.rmtree('media/uploads', ignore_errors=False, onerror=None)

            self.stdout.write('Deleting database...')
            NdrCoreValue.objects.all().delete()
            NdrCoreColorScheme.objects.all().delete()
            NdrCoreUiStyle.objects.all().delete()
            NdrCorePage.objects.all().delete()
            NdrCoreDataSchema.objects.all().delete()
            NdrCoreSearchField.objects.all().delete()
            NdrCoreSearchConfiguration.objects.all().delete()
            NdrCoreSearchFieldFormConfiguration.objects.all().delete()
            NdrCoreApiConfiguration.objects.all().delete()
            NdrCoreCorrectedField.objects.all().delete()
            NdrCoreCorrection.objects.all().delete()
            NdrCoreFilterableListConfiguration.objects.all().delete()
            NdrCoreApiImplementation.objects.all().delete()

            self.stdout.write('NDR installation deleted')
            self.stdout.write('IMPORTANT: remove "ndr" from INSTALLED_APPS in settings')

        else:
            self.stdout.write('Aborted. No changes were made')
