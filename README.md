# django_ndr_core

NDR_CORE is a django app which helps you build a web interface for your NDR data.
This repository contains the sources to the ndr_core module. You don't need to clone
or download it in order to use ndr_core. If you want to build your own ndr web interface,
follow the instructions below

## How to use ndr_core
Follow these step-by-step instructions to create your own ndr installation.

1. Create a base directory
```
mkdir <projectname>
cd <projectname>
```

2. Make sure you have Python and pip installed
```
python3 --version
pip3 --version
```

If installed, a version number is shown. If not, follow the next step

3. Install python and pip
```
sudo apt-get update
sudo apt-get install python3.8
sudo apt-get -y install python3-pip
```

4. Create a virtual environment
```
sudo pip3 install virtualenv 
virtualenv venv 
```

5. Activate the virtual environment

6. Install ndr_core
```
pip install django-ndr-core
```

7. Start a django project
```
django-admin startproject <projectname>
python manage.py migrate
python manage.py init_ndr_core
```