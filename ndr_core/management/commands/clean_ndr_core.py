import os
import shutil

from django.core.management.base import BaseCommand

from ndr_core.models import NdrCoreValue, NdrCorePage, NdrCoreDataSchema, NdrCoreSearchField
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

                NdrCoreValue.objects.all().delete()
                NdrCorePage.objects.all().delete()
                NdrCoreDataSchema.objects.all().delete()
                NdrCoreSearchField.objects.all().delete()

                self.stdout.write('NDR installation deleted')
                self.stdout.write('IMPORTANT: remove "ndr" from INSTALLED_APPS in settings')
            else:
                self.stdout.write('Aborted. No installation found')
        else:
            self.stdout.write('Aborted. No changes were made')
