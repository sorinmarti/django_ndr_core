import os

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'This command '

    def add_arguments(self, parser):
        parser.add_argument('app_name', type=str)

    def handle(self, *args, **options):
        app_name = options['app_name']

        # Check if app exists
        if not os.path.isdir(app_name):
            self.stdout.write(self.style.ERROR('Did not find app directory.'
                                               ' Create the app using the "startapp" command.'))
            return

        # Get additional data
        app_label = ''
        while not app_label:
            app_label = input(f'What is the title of your app "{app_name}"? ')

        short_description = input(f'Provide a short description: ')

        app_path = ''
        while not app_path:
            app_path = input(f'What is the base URL path your app "{app_name}"? ')


        self.stdout.write(self.style.SUCCESS('Finished.'))
