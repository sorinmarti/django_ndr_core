===============
Django NDR Core
===============

Django NDR Core is a Django app to create a web frontend for a NDR (New Data Repository) system.

Quick start
-----------

1. Add the following entries to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'ndr_core',
        'django_tables2',
        'crispy_forms',
        'django_select2',
        'bootstrap4',
        'ckeditor',
        'ckeditor_uploader',
        'captcha',
        'colorfield',
        'fontawesomefree',
    ]

2. Include the necessary URL configs in your project urls.py like this::

    path('ndr_core/', include('ndr_core.urls')),
    path("select2/", include("django_select2.urls")),
    re_path(r'^ckeditor/', include('ckeditor_uploader.urls')),

3. Run ``python manage.py migrate`` to create the polls models.

4. Start the development server and visit http://127.0.0.1:8000/ndr_core/
   to start configuring your NDR frontend.

5. Visit http://127.0.0.1:8000/
    to see your NDR frontend.