![Codecov branch](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/wiki/lawandorga/lawandorga-backend/python-coverage-comment-action-badge.json)

# Law&Orga

Law&Orga is a project of Refugee Law Clinics Deutschland e.V.

## General

This is the main backend service of Law&Orga.

Special thanks to Dominik Walser who was the first developer on this project.

© AGPL-3.0

## Tech

This project uses Django, which is based on python.

## Pre Setup

Install the required Python packages:

`pip install Django pytz oidc-provider djangorestframework pydantic django-storages django-solo django-cors-headers ics cryptography bleach pyotp whitenoise duspython weasyprint argon2-cffi`

### Local Setup

1. `git clone https://github.com/lawandorga/lawandorga-backend-service.git`
2. `cd lawandorga-backend-service`
3. `pipenv install`
4. Create `tmp/media/`, `tmp/static/`, `tmp/logs`
5. Run `pipenv shell`
6. Run `python manage.py migrate`
7. Run `python manage.py create_dummy_data`
8. Run `python manage.py runserver`

The command `create_dummy_data` creates an user with email `dummy@law-orga.de` and password `qwe123`. You can use it to login into the development frontend.

### Local Dev

1. `git pull`
2. `pipenv install`
3. `python manage.py migrate`
4. `python manage.py runserver`

### Server Setup

You might want to look into the following file `.github/workflows/deploy.yml`. This workflow file tests the application
and afterwards it builds and pushes the image into a docker registry. From that registry you can deploy the image to the
hoster of your choice. Some environment variables need to be set within the running environment.

#### Needed Environment Variables

```
DB_NAME=""
DB_USER=""
DB_PASSWORD=""
DB_PORT=""
DB_HOST=""
DJANGO_SECRET_KEY=""
EMAIL_ADDRESS=""
EMAIL_HOST=""
EMAIL_PASSWORD=""
EMAIL_PORT=""
PIPELINE_IMAGE=""
PIPELINE_SERVICE=""
S3_ACCESS_KEY=""
S3_BUCKET_NAME=""
S3_SECRET_KEY=""
```
