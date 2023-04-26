# NDR Core Ubuntu installation guide
This guide will help you install NDR Core on a Ubuntu server. It will also help you create your first presentation website.
The setup is as follows:

- Ubuntu 22.04 LTS server
- Nginx webserver
- Gunicorn
- MongoDB
- NDR Core django application
- SQLite database for NDR Core
- IIIF Image Server

This will allow you to create a presentation website where you store your data and your source imagery on the same
server. This is not recommended for production use. For production use you should use a separate server for your
source imagery. Ideally it should be stored in a long term repository like InvenioRDM.

This guide is tested for a Ubuntu 22.04 LTS server installation. It should work for other versions of Ubuntu as well
but the mongodb installation may differ.

## Prerequisites
This guide assumes you have a working Ubuntu 22.04 LTS server installation. If you don't have one you can follow
this guide to install one: https://www.digitalocean.com/community/tutorials/initial-server-setup-with-ubuntu-22-04

## Basic Setup
First you need to install the basic packages. You need to install Python, pip, virtualenv, git, nginx, curl,
postgresql and the IIIF Image Server (cantaloupe). 

Django is a Python web framework. You need to install Python and pip. Django and NDR Core are installed
within a virtual python environment. Nginx is a webserver that will serve our application. Curl is used to 
download the IIIF Image Server.

Django can run with different database backends. We will use SQLite for this tutorial. You can use any other
database backend you like. For production use you can use PostgreSQL or MySQL. The django-database stores the
page contents, your search and api configuration, user messages and configuration values, so it is not particularly
large or heavily used and SQLite is fine most of the time. For more information on other databases see
https://docs.djangoproject.com/en/3.2/ref/databases/. The following command also installs PostgreSQL if you want to
use it.

```
sudo apt update
sudo apt install python3-venv python3-dev libpq-dev postgresql postgresql-contrib nginx curl
```


## Create Your Project
Create a directory for your project, change its ownership and change into it.
```
sudo mkdir /var/www/<projectname>
sudo chown <username> /var/www/<projectname>
cd /var/www/<projectname>
```

Now create a virtual environment and activate it.
```
python3 -m venv venv
source venv/bin/activate
```

In your virtual environment install django, gunicorn and ndr_core. The ``psycopg2-binary`` package is not needed
if you don't use PostgreSQL.

```
pip install django gunicorn psycopg2-binary django-ndr-core
```

## Create a Django Project
Now you can create a django project. Replace <projectname> with the name of your project.
This can be the same name as the parent directory with your virtual environment, but it hasn't
to be.

```
django-admin startproject <projectname>
```

This will create a directory with the name of your project. Change into it.
You'll find another directory with the same name inside. Change into that directory.

```
cd <projectname>/<projectname>
```

There you'll find a file called ``settings.py``. Open it with your favorite editor and make the 
following changes:

- Add the following lines to the top of the file with the other imports:
```
import os
from ndr_core.ndr_settings import *
```
- Add the following line after the INSTALLED_APPS list:
```
INSTALLED_APPS += NdrSettings.get_installed_apps()
```
- To the bottom of the file add the following lines:
```
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')
MEDIA_URL = '/media/'
```

- Now open the file ``urls.py`` and add the following line to the top of the file with the other imports:
```
from ndr_core.ndr_settings import NdrSettings
```
- Add the following line below the urlpatterns list:
```
urlpatterns += NdrSettings.get_urls()
```

- For production use, you'll have to change more settings: Set the ``ALLOWED_HOSTS`` setting to include the hostname 
of your server and set the ``DEBUG`` flag to False.

Now change back to your django project directory and create the database. This will create a file called ``db.sqlite3``
in your project directory. This is the default database for django. If you want to use PostgreSQL or MySQL you'll have
to change the ``DATABASES`` setting in the ``settings.py`` file. See https://docs.djangoproject.com/en/3.2/ref/databases/
for more information.

```
cd ..
python manage.py migrate
```



## Install mongodb

           
```
sudo apt-get install gnupg

wget -qO - https://www.mongodb.org/static/pgp/server-4.0.asc | sudo apt-key add -

curl -fsSL https://pgp.mongodb.com/server-6.0.asc | \
   sudo gpg -o /usr/share/keyrings/mongodb-server-6.0.gpg \
   --dearmor

echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-6.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list

sudo apt-get update

sudo apt-get install -y mongodb-org

sudo systemctl start mongod
sudo systemctl daemon-reload
sudo systemctl status mongod
sudo systemctl enable mongod


This tutorial will walk you through the process of installing NDR Core on your computer and creating your first presentation website.

## Prerequisites

## Installation

## 
## Creating a Presentation Website
```

## Sources

https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-ubuntu/
https://docs.djangoproject.com/
https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-22-04
https://www.digitalocean.com/community/tutorials/how-to-install-java-with-apt-on-ubuntu-22-04
https://www.digitalocean.com/community/tutorials/how-to-set-up-password-authentication-with-nginx-on-ubuntu-20-04
https://www.digitalocean.com/community/tutorials/how-to-secure-nginx-with-let-s-encrypt-on-ubuntu-20-04