##################
How To Get Started
##################

Before starting, make sure NDR Core is right for you. NDR Core is meant to be a frontend
to your data but it doesn't serve as a database. The typical use case is to have a database
with a REST API and then use NDR Core to build a frontend to that API. A certain API must
be implemented in NDR Core for it to work. You can add your own API implementations to NDR
Core or use one of the existing ones.
Also, you'll need a web server to host NDR Core. This means you'll need access to a VM and
you'll need a domain name. If you want to show IIIF imagery from your data, you'll need a
IIIF service to host them.

Docker Image
------------
The easiest way to get started is to use the Docker image. You can find it on Docker Hub:
https://hub.docker.com/r/sorinmarti/django-ndr-core.

To run the Docker image, you'll need to have Docker installed. You can find instructions
on how to install Docker here: https://docs.docker.com/install/.  To get the Docker image,
you'll need to run the following command:

::

        docker pull sorinmarti/django-ndr-core


Then, you can run the following command to start the Docker image

::

    docker run -p 8000:8000 sorinmarti/django-ndr-core

This will start the Docker image and expose port 8000. You can then access the NDR Core
frontend by going to http://localhost:8000.

Using the image in production is not recommended.

Server Installation
-------------------
Follow the instructions on the :doc:`install-on-a-server`. This is
recommended if you want to use NDR Core in production.

Installing from Source
----------------------
If you want to install NDR Core from source, clone the GitHib repository:

::

    gh repo clone sorinmarti/django_ndr_core

Then, install the requirements, create the database and run the migrations.
This is only necessary if you want to develop NDR Core or if you want to create
your own API implementation.