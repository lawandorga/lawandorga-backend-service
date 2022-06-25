![Codecov branch](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/wiki/lawandorga/lawandorga-backend/python-coverage-comment-action-badge.json)
[![codecov](https://codecov.io/gh/lawandorga/lawandorga-backend/branch/main/graph/badge.svg?token=3YGIYK0I70)](https://codecov.io/gh/lawandorga/lawandorga-backend)

# Law&Orga

## General

Backend for Law&Orga of (Refugee) Law Clinics in Germany

A project of Refugee Law Clinics Deutschland e.V. and Dominik Walser

© Dominik Walser, AGPL-3.0

This project contains a backend based on Django-Rest-Framework. It uses S3 as file-storage.

## Local Setup
1. `git clone https://github.com/lawandorga/law-orga-apps.git`
2. `cd law-orga-backend/`
3. `python -m venv tmp/venv`
4. Install all dependencies from `requirements.txt`
5. Create `tmp/media/`, `tmp/static/`, `tmp/logs` and `tmp/secrets.json`
6. Add relevant content into `secrets.json`
6. Run `python local_manage.py runserver`

## Server Setup
1. `cd /home`
2. `git clone https://github.com/lawandorga/law-orga-apps.git`
3. `cd law-orga-backend/`
4. Connect `prod-api.law-orga.de` with the server IP
5. `./setup.prod.sh`
6. Add content to `tmp/secrets.json`
7. `./deploy.sh`

## Secrets Local

`
{
    "SECRET_KEY": "nosecret",
    "FRONTEND_URL": "http://localhost:4200/",
    "JWT_SIGNING_KEY": "nosecret"
}
`

## Secrets Prod

`
{
    "ALLOWED_HOSTS": [],
    "CORS_ALLOWED_ORIGINS": [],
    "SECRET_KEY": "",
    "EMAIL_ADDRESS": "",
    "EMAIL_HOST": "",
    "EMAIL_HOST_PASSWORD": "",
    "EMAIL_HOST_USER": "",
    "EMAIL_PORT": 0,
    "SCW_S3_BUCKET_NAME": "",
    "SCW_ACCESS_KEY": "",
    "SCW_SECRET_KEY": "",
    "FRONTEND_URL": "",
    "DB_NAME": "",
    "DB_USER": "",
    "DB_PASSWORD": "",
    "DB_PORT": 0,
    "DB_HOST": "",
    "JWT_SIGNING_KEY": ""
}
`
