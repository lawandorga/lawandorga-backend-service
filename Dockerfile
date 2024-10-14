# inspired by: https://snyk.io/blog/best-practices-containerizing-python-docker/
FROM python:3.13 as base

# workdir related stuff stuff
WORKDIR /django
RUN python -m venv /django/venv
ENV PATH="/django/venv/bin:$PATH"

# install requirements
COPY Pipfile /django/Pipfile
COPY Pipfile.lock /django/Pipfile.lock
RUN pip install --upgrade pip pipenv
RUN pipenv requirements > /django/requirements.txt
RUN pip install -r /django/requirements.txt

# build image
FROM python:3.13-slim as build

# least privilege user
RUN groupadd -g 999 python && useradd -r -u 999 -g python python

# install library for psycopg2
RUN apt-get update && apt-get install libpq5 -y

# install library for weasyprint
RUN apt-get install -y --no-install-recommends build-essential libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info

# copy files
RUN mkdir /django && chown python:python /django
WORKDIR /django
COPY --chown=python:python --from=base /django/venv /django/venv
COPY --chown=python:python config /django/config
COPY --chown=python:python core /django/core
COPY --chown=python:python messagebus /django/messagebus
COPY --chown=python:python seedwork /django/seedwork
COPY --chown=python:python static /django/static
COPY --chown=python:python templates /django/templates
COPY --chown=python:python tmp /django/tmp
COPY manage.py /django/manage.py

# change to nonroot user
USER 999

# make commands available
ENV PATH="/django/venv/bin:$PATH"

# create static files
RUN python manage.py collectstatic --noinput

# run
EXPOSE 8080
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8080", "--timeout", "240", "-w", "4"]
