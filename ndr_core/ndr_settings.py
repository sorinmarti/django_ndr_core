import os.path

from django.conf import settings


class NdrSettings:
    APP_NAME = 'ndr'

    ADDITIONAL_APPS = [
        'ndr_core',
        'django_tables2',
        'crispy_forms',
        'django_select2',
        'bootstrap4',
        'crispy_bootstrap4',
        'ckeditor',
        'ckeditor_uploader',
        'captcha',
        'colorfield',
        'fontawesomefree',
        'django.forms',
    ]

    @staticmethod
    def app_exists():
        return os.path.isdir(f"{NdrSettings.APP_NAME}/")

    @staticmethod
    def get_installed_apps():
        apps = NdrSettings.ADDITIONAL_APPS
        if NdrSettings.app_exists():
            apps.append(NdrSettings.APP_NAME)
        return apps

    @staticmethod
    def get_templates_path():
        dir_name = f'{NdrSettings.APP_NAME}/templates/{NdrSettings.APP_NAME}'
        return dir_name

    @staticmethod
    def get_static_path():
        dir_name = f'{NdrSettings.APP_NAME}/static/{NdrSettings.APP_NAME}'
        return dir_name

    @staticmethod
    def get_files_path():
        return f"{NdrSettings.get_static_path()}/files"

    @staticmethod
    def get_data_path():
        return f"{NdrSettings.get_static_path()}/data"

    @staticmethod
    def get_sample_data_path():
        return f"{NdrSettings.get_static_path()}/sample_data"

    @staticmethod
    def get_images_path():
        return f"{NdrSettings.get_static_path()}/images"

    @staticmethod
    def get_css_path():
        return f"{NdrSettings.get_static_path()}/css"

    @staticmethod
    def app_registered():
        return NdrSettings.APP_NAME in settings.INSTALLED_APPS

    @staticmethod
    def app_in_urls():
        settings_module = os.environ.get('DJANGO_SETTINGS_MODULE')
        project_name = settings_module.split(".")[0]

        with open(f'{project_name}/urls.py') as urls_file:
            for line in urls_file.readlines():
                search_for = f"{NdrSettings.APP_NAME}.urls"
                if search_for in line and not '#' in line[0:line.find(search_for)]:
                    return True
        return False
