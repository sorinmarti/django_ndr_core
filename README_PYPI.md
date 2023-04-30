# django-ndr-core

django-ndr-core is a mini CMS but most of all an access point to research data over apis.
NDR Core helps you create a project website and present your data. It lets you create
pages and add content to them. It also lets you create and manage your own data access
points over different APIs and lets you configure how to present the data and how to make
it searchable.

[![PyPI version](https://badge.fury.io/py/django-ndr-core.svg)](https://badge.fury.io/py/django-ndr-core)
[![Docker Image CI](https://github.com/sorinmarti/django_ndr_core/actions/workflows/docker-image.yml/badge.svg)](https://github.com/sorinmarti/django_ndr_core/actions/workflows/docker-image.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Get Started
- Find the [Documentation](https://django-ndr-core.readthedocs.io/en/latest/) on ReadTheDocs.

#### settings.py
Open ```<project_name>/settings.py``` and add the ndr_core module and its dependencies to ```INSTALLED_APPS```:
(Leave the existing settings in place).

```python
import os
from ndr_core.ndr_settings import *

[...]

INSTALLED_APPS = [
    [...]
]
INSTALLED_APPS += NdrSettings.get_installed_apps()
```

#### urls.py
Open ```<project_name>/urls.py``` and add the ndr_core module and its dependencies to ```INSTALLED_APPS```:
(Leave the existing settings in place).
```python
from ndr_core.ndr_settings import NdrSettings

[...]

urlpatterns = [
   [...]
]
urlpatterns += NdrSettings.get_urls()
```

#### Migrate the database
After you have added the django-ndr-core module and its dependencies to your settings and urls, 
you can migrate your installation again to create the necessary database tables for your 
ndr-core installation.

```shell
python manage.py migrate
python manage.py collectstatic
```

#### Initialize your NDR Core app

```shell
python manage.py init_ndr_core
```

#### Start configuring and entering content
Run your server.
    
```shell
python manage.py runserver
```

Visit http://localhost:8000/ to view your website and http://localhost:8000/ndr_core/ 
to access the configuration interface. The last command runs your server on port 8000.
This is not suitable for production use. You should use a webserver like nginx to serve
your application. See the [Documentation](https://django-ndr-core.readthedocs.io/en/latest/) for more information.