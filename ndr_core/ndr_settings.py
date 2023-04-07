import os.path

from django.conf import settings
from django.urls import path, include, re_path, reverse_lazy
from django.views.static import serve
from django.contrib import messages


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
        'bootstrap_daterangepicker'
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
    def get_urls():
        urls = [
            path('ndr_core/', include('ndr_core.urls')),
            path("select2/", include("django_select2.urls")),
            re_path(r'^ckeditor/', include('ckeditor_uploader.urls'))
        ]

        if NdrSettings.app_exists():
            urls += [path('', include(f'{NdrSettings.APP_NAME}.urls')),]

        if settings.DEBUG:
            urls += [
                re_path(r'^media/(?P<path>.*)$', serve, {
                    'document_root': settings.MEDIA_ROOT
                }),
            ]

        return urls


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


CRISPY_TEMPLATE_PACK = 'bootstrap4'
DJANGO_TABLES2_TEMPLATE = "django_tables2/bootstrap4.html"

LOGIN_URL = reverse_lazy('ndr_core:login')
LOGOUT_URL = reverse_lazy('ndr_core:logout')
LOGIN_REDIRECT_URL = reverse_lazy('ndr_core:dashboard')

FORM_RENDERER = 'django.forms.renderers.TemplatesSetting'



MESSAGE_TAGS = {
        messages.DEBUG: 'alert-secondary',
        messages.INFO: 'alert-info',
        messages.SUCCESS: 'alert-success',
        messages.WARNING: 'alert-warning',
        messages.ERROR: 'alert-danger',
}

RECAPTCHA_PUBLIC_KEY = '6LdIoTwkAAAAAMoxg2s9vvLklOy0QY92q9cdionT'
RECAPTCHA_PRIVATE_KEY = '6LdIoTwkAAAAAAyfC5D4cpvqjCRUDxKoz5BtWyM0'

CKEDITOR_UPLOAD_PATH = 'uploads/'

