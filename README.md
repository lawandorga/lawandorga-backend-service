![Codecov branch](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/wiki/lawandorga/lawandorga-backend/python-coverage-comment-action-badge.json)

# Law&Orga

## General

Backend for Law&Orga of (Refugee) Law Clinics in Germany

A project of Refugee Law Clinics Deutschland e.V. and Dominik Walser

© Dominik Walser, AGPL-3.0

This project contains a backend based on Django-Rest-Framework. It uses Amazon S3 as file-storage.

## Local setup
1. `git clone https://github.com/lawandorga/law-orga-apps.git`
2. `cd law-orga-backend/`
3. `python -m venv tmp/venv`
4. Install all dependencies from `requirements.txt`
5. Create `tmp/media/`, `tmp/static/`, `tmp/logs` and `tmp/secrets.json`
6. Add relevant content into `secrets.json`   
6. Run `python local_manage.py runserver`

## Server setup
1. `cd /home`
2. `git clone https://github.com/lawandorga/law-orga-apps.git`
3. `cd law-orga-backend/`
4. Connect `prod-api.law-orga.de` with the server IP
5. `./setup.prod.sh`
6. Add content to `tmp/secrets.json`   
7. `./deploy.sh`

## Secrets dev

`
{

}
`
