![Codecov branch](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/wiki/lawandorga/lawandorga-backend/python-coverage-comment-action-badge.json)

# Law&Orga

Law&Orga is a project of Refugee Law Clinics Deutschland e.V.

## General

This is the main backend service of Law&Orga.

Special thanks to Dominik Walser who was the first developer on this project.

© AGPL-3.0

## Tech

This project uses Django, which is based on python.

### Local Setup

1. `git clone https://github.com/lawandorga/law-orga-apps.git`
2. `cd law-orga-backend/`
3. `python -m venv tmp/venv`
4. Install all dependencies from `requirements.txt` with `pip install -r requirements.txt`
5. Create `tmp/media/`, `tmp/static/`, `tmp/logs`
6. Run `python manage.py runserver`

### Server Setup

You might want to look into the following file: `.github/workflows/deploy.yml`. You need to set some environment
variables and with them the workflow file pushes a docker container into a docker registry. From that registry you can
deploy the image to the hoster of your choice. Some environment variables need to be set within the running environment.

### Environment Variables

`
ALLOWED_HOSTS=""
CORS_ALLOWED_ORIGINS=""
SECRET_KEY=""
EMAIL_ADDRESS=""
EMAIL_HOST=""
EMAIL_PASSWORD=""
EMAIL_PORT=""
S3_BUCKET_NAME=""
S3_ACCESS_KEY=""
S3_SECRET_KEY=""
FRONTEND_URL=""
DB_NAME=""
DB_USER=""
DB_PASSWORD=""
DB_PORT=""
DB_HOST=""
JWT_SIGNING_KEY=""
`
