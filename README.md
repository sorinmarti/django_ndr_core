# django_ndr_core

NDR_CORE is a django app which helps you build a web interface for your NDR data.
This repository contains the sources to the ndr_core module. You don't need to clone
or download it in order to use ndr_core. If you want to build your own ndr web interface,
follow the instructions below

## How to use ndr_core (in this creation phase)
1. Clone the repo, create and activate a virtual environment
2. Install requirements: ```pip install -r requirements.txt``` 
3. Create Sqlite Database: ```python manage.py migrate```
4. Collect static files: ```python manage.py collectstatic``` (might take a while)
5. Init your NDR page: ```python manage.py init_ndr_core```
6. Run your server: ```python manage.py runserver```

You should be able to access your site now. It consists of a simple home page.
![image](https://user-images.githubusercontent.com/32014438/203301471-24935756-0d4a-4926-9faa-db1dcbb3bc72.png)

Go to http://localhost:8000/ndr_core/ to configure your page.

## How to use ndr_core (in the future)
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
