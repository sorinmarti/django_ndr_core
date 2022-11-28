import os.path

from django.conf import settings


class NdrSettings:
    APP_NAME = 'ndr'

    @staticmethod
    def app_exists():
        return os.path.isdir(f"{NdrSettings.APP_NAME}/")

    @staticmethod
    def app_registered():
        return NdrSettings.APP_NAME in settings.INSTALLED_APPS

    @staticmethod
    def app_in_urls():
        settings_module = os.environ.get('DJANGO_SETTINGS_MODULE')
        project_name = settings_module.split(".")[0]

        print(f'{project_name}')
        with open(f'{project_name}/urls.py') as urls_file:
            for line in urls_file.readlines():
                search_for = f"{NdrSettings.APP_NAME}.urls"
                if search_for in line and not '#' in line[0:line.find(search_for)]:
                    return True
        return False
