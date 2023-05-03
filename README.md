# django-ndr-core

Django NDR Core is a django app which helps you build a web interface to present your research
data. This repository contains the sources to the ndr_core module. You are free to clone
or download it, but you'll only need it if you want to develop it further (which is
highly welcomed). To use NDR Core you can install it from PyPi or check out the Docker image. 

![DjangoCI Status](https://github.com/sorinmarti/django_ndr_core/actions/workflows/django.yml/badge.svg)
![PyPi Status](https://github.com/sorinmarti/django_ndr_core/actions/workflows/python-publish.yml/badge.svg)
[![Documentation Status](https://readthedocs.org/projects/django-ndr-core/badge/?version=latest)](https://django-ndr-core.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/django-ndr-core.svg)](https://badge.fury.io/py/django-ndr-core)
![Docker Cloud Automated build](https://img.shields.io/docker/cloud/automated/sorinmarti/django-ndr-core)
![Docker Cloud Build Status](https://img.shields.io/docker/cloud/build/sorinmarti/django-ndr-core)
[![License](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)
[![DOI](https://zenodo.org/badge/541529637.svg)](https://zenodo.org/badge/latestdoi/541529637)

## More Information
- Read the [Documentation](https://django-ndr-core.readthedocs.io/en/latest/) on ReadTheDocs.
- Find the module on [PyPi](https://pypi.org/project/django-ndr-core/).
- Check out the [Docker image](https://hub.docker.com/r/sorinmarti/django_ndr_core) on Docker Hub.
- See [ndrcore.org](https://ndrcore.org) for a demo and a list of projects using NDR Core. (in development). 

## How to use NDR Core
First you need to install NDR Core. You can do this in different ways. You can install it from PyPi, you can use the
Docker image or you can clone this repository and install it from the sources.

It is recommended to use the docker image for local testing and configuration. For production use you should install
NDR Core from PyPi and use a webserver like nginx to serve the application.

### Use the Docker image
The Docker image is available on Docker Hub. You can pull it with the following command:
```shell
docker pull sorinmarti/django_ndr_core
```
You can run the image with the following command:
```shell
docker run -p 8000:8000 sorinmarti/django_ndr_core
```
This will start the application on port 8000. You can access it with your browser on http://localhost:8000.


### Install NDR Core from Scratch
This is a step-by-step guide to install NDR Core on a Ubuntu Machine (or similar). It is recommended to use a virtual environment
for the installation. This guide assumes that you have a fresh Ubuntu installation. If you already have Python and
pip installed, you can skip the first two steps.

#### Make sure you have Python and pip installed, update pip to the latest version
```shell
python3 --version
pip3 --version
python3 -m pip install --upgrade pip
```
If installed, a version number is shown. If not, follow the next step

#### Install python and pip
```shell
sudo apt-get update
sudo apt-get install python3.11
sudo apt-get -y install python3-pip
```

#### Create a project directory
Create a directory for your project and change into it. This will be the root directory of your project.
It contains the virtual environment and the django project.
```shell
mkdir <project_root>
cd <project_root>
```

#### Create a virtual environment
```shell
pip3 install virtualenv 
virtualenv venv 
```

#### Activate the virtual environment and upgrade pip
```shell
source venv/bin/activate
python -m pip install --upgrade pip
```

#### Install ndr_core
This will install all the needed dependencies and also install django.
```shell
pip install django-ndr-core
```

#### Start a django project
Replace `<project_name>` with the name of your project. It can be the same as your project root directory.
```shell
django-admin startproject <project_name>
cd <project_name>
```

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
After you have added the django-ndr-core module and its dependencies to your settungs and urls, you can migrate your installation again to create the necessary database tables for your ndr-core installation.

```shell
python manage.py migrate
python manage.py collectstatic
```

#### Initialize your NDR Core app
Django works as such that there are different apps. django-ndr-core is a django-app which lets you create and manage your own app. Use the following command initialize your own.

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
