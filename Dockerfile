# syntax=docker/dockerfile:1.4

# The first instruction is what image we want to base our container on
# We Use an official Python runtime as a parent image
FROM python:3.10

# The enviroment variable ensures that the python output is set straight
# to the terminal with out buffering it first
ENV PYTHONUNBUFFERED 1

# create root directory for our project in the container
RUN mkdir /ndr_core_service

# Set the working directory to /ndr_core_service
WORKDIR /ndr_core_service

# Copy the current directory contents into the container at /ndr_core_service
ADD . /ndr_core_service/

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt --no-cache-dir
RUN pip install gunicorn

RUN python manage.py makemigrations
RUN python manage.py migrate
RUN python manage.py collectstatic --noinput
RUN python manage.py init_ndr_core --noinput=True
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# Make port 8000 available to the world outside this container
EXPOSE 8000