##################
Installation guide
##################

This guide will help you install NDR Core on a Ubuntu server. The setup is as follows:

* Ubuntu 22.04 LTS server
* Nginx webserver
* Gunicorn
* MongoDB
* Django and NDR Core application
* SQLite database for NDR Core
* Cantaloupe IIIF Image Server

This will allow you to create a presentation website where you store your data and your
source imagery on the same server. This is not recommended for production use. For production
use you should use a separate server for your source imagery. Ideally it should be stored in a
long term repository like InvenioRDM or Zenodo.

This guide is tested for a Ubuntu 22.04 LTS server installation. It should work for other versions of
Ubuntu as well but the mongodb installation may differ.

Most of the steps in this guide are not specific to NDR Core. This guide provides a full setup
for a django application, serving it with gunicorn and nginx.

Prerequisites
=============
This guide assumes you have a working Ubuntu 22.04 LTS server installation. If you don't have one you can follow
this guide to install one: https://www.digitalocean.com/community/tutorials/initial-server-setup-with-ubuntu-22-04

Basic Setup
===========
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

.. code-block:: bash

    sudo apt update
    sudo apt install python3-venv python3-dev libpq-dev postgresql postgresql-contrib nginx curl


Create Your Project
===================
Create a directory for your project, change its ownership and change into it.

.. code-block:: bash

    sudo mkdir /var/www/<project_root>
    sudo chown <username> /var/www/<project_root>
    cd /var/www/<projectname>


Now create a virtual environment and activate it.

.. code-block:: bash

    python3 -m venv venv
    source venv/bin/activate


In your virtual environment install django, gunicorn and ndr_core. The `psycopg2-binary` package is not needed
if you don't use PostgreSQL.


.. code-block:: bash

    pip install django gunicorn psycopg2-binary django-ndr-core


Create a Django Project
-----------------------
Now you can create a django project. Replace <projectname> with the name of your project.
This can be the same name as the parent directory with your virtual environment, but it hasn't
to be.

.. code-block:: bash

    django-admin startproject <projectname>

This will create a directory with the name of your project. Change into it.
You'll find another directory with the same name inside. Change into that directory.

.. code-block:: bash

    cd <projectname>/<projectname>


There you'll find a file called ``settings.py``. Open it with your favorite editor and make the
following changes:

Add the following lines to the top of the file with the other imports:

.. code-block:: python

    import os
    from ndr_core.ndr_settings import *

Add the following line after the INSTALLED_APPS list:

.. code-block:: python

    INSTALLED_APPS += NdrSettings.get_installed_apps()

To the bottom of the file add the following lines:

.. code-block:: python

    STATIC_ROOT = os.path.join(BASE_DIR, 'static')
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')
    MEDIA_URL = '/media/'

Now open the file ``urls.py`` and add the following line to the top of the file with the other imports:

.. code-block:: python

    from ndr_core.ndr_settings import NdrSettings

Add the following line below the urlpatterns list:

.. code-block:: python

    urlpatterns += NdrSettings.get_urls()


Now change back to your django project directory and create the configuration database. This
database has nothing to do with your searchable data. It stores the configuration of your
search and api, user messages and configuration values. It is not particularly large or heavily used
and SQLite is fine most of the time.

.. code-block:: bash

    cd ..
    python manage.py migrate


This will create a file called ``db.sqlite3`` in your project directory. This is the default database for django.
If you want to use PostgreSQL or MySQL you'll have to change the ``DATABASES`` setting in the ``settings.py`` file.
See https://docs.djangoproject.com/en/3.2/ref/databases/ for more information.

Now we need to collect all the static files for our project. This will create a directory called ``static``
in your project directory.

.. code-block:: bash

    python manage.py collectstatic

To initialize the NDR Core system, run the following command:

.. code-block:: bash

    python manage.py init_ndr_core

You will be asked to enter some values, but don't worry, you can change them later.

Your django installation is now ready to run and all necessary settings have been made.
For production use, you'll have to change more settings: Set the ``ALLOWED_HOSTS`` setting
to include the host name of your server and set the ``DEBUG`` flag to False. Also, you might
wan to configure your captcha api key or other settings. See the django documentation for more
information: https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

To test your installation, run the following command and then visit
http://localhost:8000 in your browser. This most likely won't work if you are running your
server in a virtual machine.

.. code-block:: bash

    python manage.py runserver

On a virtual machine, you can try to open port 8000 and then visit http://<your-server-ip>:8000

.. code-block:: bash

    sudo ufw allow 8000
    python manage.py runserver 0.0.0.0:8000

You should assign ownership of the project directory to the user that will run the django project.
This is ideally ``www-data`` or something similar.

.. code-block:: bash

    sudo chown -R www-data /var/www/<project_root>

To now run your django project with gunicorn, follow the next steps.

Configure Nginx and Gunicorn
============================
First we test, if we can serve the page with gunicorn. Run the following command
(Replace <projectname> with the name of your project):

.. code-block:: bash

    gunicorn --bind 0.0.0.0:8000 <projectname>.wsgi

If gunicorn starts without errors, visit http://<your-server-ip>:8000 to check if
your page is served. It is normal that stylesheets and images are missing. We'll fix
that later.

Stop gunicorn with Ctrl-C. Exit your virtual environment and create a systemd socket and
service file for gunicorn.

.. code-block:: bash

    deactivate
    sudo nano /etc/systemd/system/gunicorn.socket

Paste the following lines into the file:

.. code-block:: bash

    [Unit]
    Description=gunicorn socket

    [Socket]
    ListenStream=/run/gunicorn.sock

    [Install]
    WantedBy=sockets.target

Now create a systemd service file for gunicorn:

.. code-block:: bash

    sudo nano /etc/systemd/system/gunicorn.service

Paste the following lines into the file:

.. code-block:: bash

    [Unit]
    Description=gunicorn daemon
    Requires=gunicorn.socket
    After=network.target

    [Service]
    User=www-data
    Group=www-data
    WorkingDirectory=/var/www/<project_root>/<projectname>
    ExecStart=/var/www/<project_root>/venv/bin/gunicorn \
              --access-logfile - \
              --workers 3 \
              --bind unix:/run/gunicorn.sock \
              <projectname>.wsgi:application

    [Install]
    WantedBy=multi-user.target

Replace <project_root> with the name of the directory where your project is located. Replace
<projectname> with the name of your project. Replace www-data with the user and group that
should run the gunicorn process. Usually this is www-data, but it might be different on your
system.

Now start and enable the gunicorn socket:

.. code-block:: bash

    sudo systemctl start gunicorn.socket
    sudo systemctl enable gunicorn.socket

You can check if the socket is running with the following command. It should show the status
of the socket and the file that it is listening on. If the socket is not running, check the
systemd logs for errors. You can also check if the file exists. If it doesn't, there is
probably an error in your gunicorn.service file.

.. code-block:: bash

    sudo systemctl status gunicorn.socket
    file /run/gunicorn.sock

With the following command, you can access the gunicorn logs:

.. code-block:: bash

    sudo journalctl -u gunicorn.socket

Until now, we have only started the gunicorn socket. The gunicorn service is not running yet
because it is only started when a connection is made to the socket. Lets proceed to configure
Nginx to Proxy Pass to the gunicorn socket.

.. code-block:: bash

    sudo nano /etc/nginx/sites-available/<projectname>

Paste the following lines into the file:

.. code-block:: nginx

    server {
        listen 80;
        server_name your-server.org;

        location = /favicon.ico { access_log off; log_not_found off; }
        location /static/ {
            root /var/www/<project_root>/<projectname>;
        }
        location /media/ {
            root /var/www/<project_root>/<projectname>;
        }

        location / {
            include proxy_params;
            proxy_pass http://unix:/run/gunicorn.sock;
        }
    }

Now enable the site, remove the default setting and test the configuration:

.. code-block:: bash

    sudo ln -s /etc/nginx/sites-available/<projectname> /etc/nginx/sites-enabled
    sudo rm /etc/nginx/sites-enabled/default
    sudo nginx -t

You should see the following output:

.. code-block:: bash

    nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
    nginx: configuration file /etc/nginx/nginx.conf test is successful

Now restart nginx:

.. code-block:: bash

    sudo systemctl restart nginx

Now we need to configure the firewall to allow connections to port 80. We can delete
the configuration for port 8000, because we won't need it anymore.

.. code-block:: bash

    sudo ufw delete allow 8000
    sudo ufw allow 'Nginx Full'

Now you should be able to visit your page in your browser but it is served with http.
To enable https, we need to install certbot.

Install certbot
===============
Certbot is provided by the certbot snap package.

.. code-block:: bash

    sudo snap install core; sudo snap refresh core

If you’re working on a server that previously had an older version of certbot installed,
you should remove it before going any further.

.. code-block:: bash

    sudo apt-get remove certbot

Now install certbot:

.. code-block:: bash

    sudo snap install --classic certbot

Finally, link the certbot command to certbot-auto:

.. code-block:: bash

    sudo ln -s /snap/bin/certbot /usr/bin/certbot

Now we can request a certificate from Let's Encrypt. Replace <your-domain> with your domain
name. If you have multiple domains, you can add them with the -d option. Certbot will ask
you to enter your email address and to agree to the terms of service. Certbot will also ask
you if you want to redirect all http traffic to https. If you want to do that, choose option 2.

.. code-block:: bash

    sudo certbot --nginx -d <your-domain>

You should activate the certificate renewal service. Currently it is not active.
Check the status of the timer:

.. code-block:: bash

    sudo systemctl status snap.certbot.renew.service

To test the renewal process, you can run the following command:

.. code-block:: bash

    sudo certbot renew --dry-run

If you see no errors, the renewal process is working fine. When necessary, Certbot will
renew your certificates and reload Nginx to pick up the changes. If the automated renewal
process ever fails, Let’s Encrypt will send a message to the email you specified, warning
you when your certificate is about to expire.

.. note::
    Your NDR Core installation is now complete. If your data and source imagery is stored
    in different places, you're all set.

    If you want to store your data and source imagery in the same place, you need to
    install a data service and a IIIF server. See the next sections for instructions.


Install MongoDB
===============
To install MongoDB Community Edition, you can follow the instructions on the MongoDB website
or follow the instructions below.

.. code-block:: bash

    sudo apt-get install gnupg

    curl -fsSL https://pgp.mongodb.com/server-6.0.asc | \
       sudo gpg -o /usr/share/keyrings/mongodb-server-6.0.gpg \
       --dearmor

    echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-6.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list

    sudo apt-get update

    sudo apt-get install -y mongodb-org

You now have installed gnupg, added the MongoDB GPG key to your system, created a list file
for MongoDB, updated the local package list and installed the MongoDB packages.

Reload systemd and start MongoDB:

.. code-block:: bash

    sudo systemctl daemon-reload
    sudo systemctl start mongod
    sudo systemctl status mongod

You can stop it with the following command:

.. code-block:: bash

    sudo systemctl start mongod

If you want it to run as a service, you can enable it with the following command:

.. code-block:: bash

    sudo systemctl enable mongod

Your MongoDB installation is now complete.

Cantaloupe IIIF Server
======================
Cantaloupe is an open-source IIIF image server. It is written in Java and uses the
Java Advanced Imaging (JAI) library. It is fast, scalable, and easy to deploy.

First, we need to install Java or check if it is installed. We will work with OpenJDK 11.

Check if Java is installed:
.. code-block:: bash

    java -version

If it is not installed, install it with the following command:
.. code-block:: bash

    sudo apt install default-jre

Change into the /usr/local/ directory and download the latest version of Cantaloupe:

.. code-block:: bash

    cd /usr/local
    sudo mkdir cantaloupe
    cd cantaloupe
    wget https://github.com/cantaloupe-project/cantaloupe/releases/download/v5.0.5/cantaloupe-5.0.5.zip

Unzip the file, cd into the directory and copy the cantaloupe.properties.sample file:

.. code-block:: bash

    unzip cantaloupe-5.0.5.zip
    cd cantaloupe-5.0.5
    cp cantaloupe.properties.sample cantaloupe.properties

Create a directory to store the images:

.. code-block:: bash

    sudo mkdir /var/www/<project_root>>/images

Open the cantaloupe.properties file and change at least the following settings:

.. code-block:: bash

    FilesystemSource.BasicLookupStrategy.path_prefix = /var/www/<project_root>/images/

If you want you can activate the admin interface:

.. code-block:: bash

    # Enables the Control Panel, at /admin.
    endpoint.admin.enabled = true
    endpoint.admin.username = admin
    endpoint.admin.secret = s3cr3t

Now you can test if cantaloupe is working:

.. code-block:: bash

    java -Dcantaloupe.config=cantaloupe.properties -Xmx2g -jar cantaloupe-5.0.5.jar

If it works, we can create a service file for Cantaloupe:

.. code-block:: bash

    sudo nano /etc/systemd/system/cantaloupe.service

Add the following content to the file:

.. code-block:: bash

    [Unit]
    Description=Cantaloupe IIIF Service

    [Service]
    User=www-data
    WorkingDirectory=/usr/local/cantaloupe/cantaloupe-5.0.5
    ExecStart=/usr/local/cantaloupe/cantaloupe-5.0.5/start-cantaloupe
    SuccessExitStatus=143
    TimeoutStopSec=10
    Restart=on-failure
    RestartSec=5

    [Install]
    WantedBy=multi-user.target

Now we need to create the start script:

.. code-block:: bash

    sudo nano /usr/local/cantaloupe/cantaloupe-5.0.5/start-cantaloupe

Add the following content to the file:

.. code-block:: bash

    #!/bin/bash
    /usr/bin/java -Dcantaloupe.config=cantaloupe.properties -Xmx2g -jar cantaloupe-5.0.5.jar

Make the script executable:

.. code-block:: bash

    sudo chmod u+x /usr/local/cantaloupe/cantaloupe-5.0.5/start-cantaloupe

Now change ownership of the cantaloupe directory:

.. code-block:: bash

    sudo chown -R www-data:www-data /usr/local/cantaloupe

Reload systemd and start Cantaloupe:

.. code-block:: bash

    sudo systemctl daemon-reload
    sudo systemctl start cantaloupe
    sudo systemctl status cantaloupe

Enable it as a service:

.. code-block:: bash

    sudo systemctl enable cantaloupe

Allow the cantaloupe port in the firewall:

.. code-block:: bash

    sudo ufw allow 8182/tcp

Add images to your image directory and test if Cantaloupe is working. Sy you have an
image called test.jpg in your image directory. You can now access it with the following
URL: http://<your_domain>:8182/iiif/3/test.jpg/full/full/0/default.jpg

You can also access the admin interface with the following URL: http://<your_domain>:8182/admin

Next Steps
==========
You now have installed NDR Core and if needed MongoDB and a IIIF image server. The
next steps are to populate the database with data and the images folder with images.

See :doc:`sample-data-base` for an example on how to populate the database.

Sources
=======
This guide heavily relies on the following sources:

* https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-ubuntu/
* https://docs.djangoproject.com/
* https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-22-04
* https://www.digitalocean.com/community/tutorials/how-to-secure-nginx-with-let-s-encrypt-on-ubuntu-22-04
* https://www.digitalocean.com/community/tutorials/how-to-install-java-with-apt-on-ubuntu-22-04
* https://www.digitalocean.com/community/tutorials/how-to-set-up-password-authentication-with-nginx-on-ubuntu-20-04
* https://www.digitalocean.com/community/tutorials/how-to-secure-nginx-with-let-s-encrypt-on-ubuntu-20-04
* https://cantaloupe-project.github.io/
* https://training.iiif.io/intro-to-iiif/INSTALLING_CANTALOUPE.html
* https://medium.com/@sulmansarwar/run-your-java-application-as-a-service-on-ubuntu-544531bd6102
