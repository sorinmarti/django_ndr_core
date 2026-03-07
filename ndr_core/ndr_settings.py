"""This file holds the NdrSettings class."""
import os.path
from pathlib import Path
from django.conf import settings
from django.urls import path, include, re_path
from django.views.static import serve


class NdrSettings:
    """Contains mostly static, mostly django-related settings. Not to be confused with NdrCoreValue objects
    which are used to set all web page and search-related settings. """

    APP_NAME = 'ndr'
    """ The generated content for the web site is technically a django-app which needs a name. This name is important 
    as it is part of all paths and view names."""

    ADDITIONAL_APPS = [
        'ndr_core',
        'django_tables2',
        'crispy_forms',
        'django_select2',
        'django_bootstrap5',
        'crispy_bootstrap5',
        'django_ckeditor_5',
        'django_recaptcha',
        'colorfield',
        'fontawesomefree',
        'django.forms',
        'bootstrap_daterangepicker',
    ]
    """NDR Core uses many third party modules which need to be in the INSTALLED_APPS list in the django settings. 
    To make things easier for users, this list is joined with the installed apps list."""

    @staticmethod
    def get_version():
        """Returns the version of the NDR Core app. """
        with open(os.path.join(Path(__file__).resolve().parent, 'VERSION'), encoding='utf8') as version_file:
            return version_file.read().strip()

    @staticmethod
    def app_exists():
        """Check if an app with the NDR app name already exists.
        Used to make sure nothing is overwritten when generating the initial web page."""
        return os.path.isdir(f"{NdrSettings.APP_NAME}/")

    @staticmethod
    def get_installed_apps():
        """Returns the additional apps to add to the INSTALLED_APPS list. Only adds the ndr-app if it already
        has been created."""
        apps = NdrSettings.ADDITIONAL_APPS
        if NdrSettings.app_exists():
            apps.append(NdrSettings.APP_NAME)
        return apps

    @staticmethod
    def get_urls():
        """Compiles a list of url paths to be used by the django base urls.py files. Only adds the ndr-app if it already
        has been created."""

        urls = [
            path('ndr_core/', include('ndr_core.urls')),
            path("select2/", include("django_select2.urls")),
            path("ckeditor5/", include('django_ckeditor_5.urls'))
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
        """Returns the ndr-app's template path. Convenience method. """
        dir_name = f'{NdrSettings.APP_NAME}/templates/{NdrSettings.APP_NAME}'
        return dir_name

    @staticmethod
    def get_static_path():
        """Returns the ndr-app's static path. Convenience method. """
        dir_name = f'{NdrSettings.APP_NAME}/static/{NdrSettings.APP_NAME}'
        return dir_name

    @staticmethod
    def get_schema_path():
        """Returns the ndr-app's static path. Convenience method. """
        dir_name = f'{settings.MEDIA_ROOT}/schemas'
        return dir_name

    @staticmethod
    def get_static_html_path():
        """Returns the ndr-app's static html path. Convenience method. """
        dir_name = f'{settings.MEDIA_ROOT}/uploads/html'
        return dir_name

    @staticmethod
    def get_images_path():
        """Returns the ndr-app's image path. Convenience method. """
        return f"{NdrSettings.get_static_path()}/images"

    @staticmethod
    def get_css_path():
        """Returns the ndr-app's css path. Convenience method. """
        return f"{NdrSettings.get_static_path()}/css"
