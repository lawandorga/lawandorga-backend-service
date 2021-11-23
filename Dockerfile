FROM python:3.9

ENV PYTHONUNBUFFERED 1

WORKDIR /django

COPY requirements.txt /django/requirements.txt
COPY tmp/secrets.json /django/tmp/secrets.json

RUN pip install -r requirements.txt

COPY . /django

RUN python manage.py collectstatic --noinput
RUN python manage.py migrate

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--timeout", "240"]
