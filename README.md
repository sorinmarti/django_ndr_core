# django_ndr_core

NDR_CORE is a django app which helps you build a web interface for your NDR data.
This repository contains the sources to the ndr_core module. You don't need to clone
or download it in order to use ndr_core. If you want to build your own ndr web interface,
follow the instructions below

![DjangoCI Status](https://github.com/sorinmarti/django_ndr_core/actions/workflows/django.yml/badge.svg)
[![Documentation Status](https://readthedocs.org/projects/django-ndr-core/badge/?version=latest)](https://django-ndr-core.readthedocs.io/en/latest/?badge=latest)

## How to use ndr_core
This is the development repo for ndr-core. Follow these step-by-step instructions to create your own ndr installation from the last release on PyPi.

### Install a python environment

#### 1.1. Create a project directory
```
mkdir <projectname>
cd <projectname>
```

#### 1.2. Make sure you have Python and pip installed, update pip to the latest version
```
python3 --version
pip3 --version
python3 -m pip install --upgrade pip
```
If installed, a version number is shown. If not, follow the next step

#### 1.3. Install python and pip
```
sudo apt-get update
sudo apt-get install python3.11
sudo apt-get -y install python3-pip
```

#### 1.4. Create a virtual environment
(You might need to sudo this command).
```
pip3 install virtualenv 
virtualenv venv 
```

#### 1.5. Activate the virtual environment and upgrade pip
```
source venv/bin/activate (linux & MacOS
venv\Scripts\activate (windows)
python -m pip install --upgrade pip
```

### Create a Django project

#### 2.1. Install ndr_core
This will install all the needed dependencies and also install django.
```
pip install django-ndr-core
```

(Or install from test.pypi:)
```
python -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ django-ndr-core
```

#### 2.2. Start a django project
Replace <projectname> with the name of your project.
```
django-admin startproject <projectname>
cd <projectname>
python manage.py migrate
```

#### 2.3. Include NDR Core into your project

##### settings.py
Open ```<projectname>/settings.py``` and add the ndr_core module and its dependencies to ```INSTALLED_APPS```:
(Leave the existing settings in place).
```
INSTALLED_APPS = [
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
    [...]
]
```

Specify the various settings from the various
```
import os
from django.contrib import messages
from django.urls import reverse_lazy

STATIC_ROOT = os.path.join(BASE_DIR, 'static')

LOGIN_URL = reverse_lazy('ndr_core:login')
LOGOUT_URL = reverse_lazy('ndr_core:logout')
LOGIN_REDIRECT_URL = reverse_lazy('ndr_core:dashboard')
FORM_RENDERER = 'django.forms.renderers.TemplatesSetting'

CRISPY_TEMPLATE_PACK = 'bootstrap4'
DJANGO_TABLES2_TEMPLATE = "django_tables2/bootstrap4.html"

MESSAGE_TAGS = {
        messages.DEBUG: 'alert-secondary',
        messages.INFO: 'alert-info',
        messages.SUCCESS: 'alert-success',
        messages.WARNING: 'alert-warning',
        messages.ERROR: 'alert-danger',
}

MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')
MEDIA_URL = '/media/'

CKEDITOR_UPLOAD_PATH = 'uploads/'

GEOIP_PATH = os.path.join(BASE_DIR, 'geoip/')
```

NDR Core forms use reCaptchas. In order to use them, you need an [API key](|https://www.google.com/recaptcha/about/).

You can sign up and enter your keys:

```
RECAPTCHA_PUBLIC_KEY = 'YourPublicKey'
RECAPTCHA_PRIVATE_KEY = 'YourPrivateKey'
```

or you can skip this step by silencing the error

```
SILENCED_SYSTEM_CHECKS = ['captcha.recaptcha_test_key_error']
```

##### urls.py
Open ```<projectname>/urls.py``` and add the needed url configs to ```urlpatterns```:

```
from django.urls import path, include, re_path

urlpatterns = [
    path('ndr_core/', include('ndr_core.urls')),
    path("select2/", include("django_select2.urls")),
    re_path(r'^ckeditor/', include('ckeditor_uploader.urls')),
    [...]
]
```

### Create Your App

#### 3.1. Migrate the database
After you have added the django-ndr-core module and its dependencies to your settungs and urls, you can migrate your installation again to create the necessary database tables for your ndr-core installation.

```
python manage.py migrate
python manage.py collectstatic
```

### 3.2. Initialize your NDR Core app
Django works as such that there are different apps. django-ndr-core is a django-app which lets you create and manage your own app. Use the following command initialize your own.

```
python manage.py init_ndr_core
```

### 3.3. Start configuring and entering content
Run your server.
    
```
python manage.py runserver
```

Visit http://localhost:8000/ to view your website and http://localhost:8000/ndr_core/ to access the configuration interface.
    

## How to use ndr_core for development
1. Clone this repo, create and activate a virtual environment
2. Install requirements: ```pip install -r requirements.txt``` 
3. Create Sqlite Database: ```python manage.py migrate```
4. Collect static files: ```python manage.py collectstatic```
5. Init your NDR page: ```python manage.py init_ndr_core```
6. Run your server: ```python manage.py runserver```

You should be able to access your site now. It consists of a simple home page.

Go to http://localhost:8000/ndr_core/ to configure your page.

(This document needs to be updated)
