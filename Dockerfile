FROM python:3.8-alpine3.13

RUN apk update && apk add --no-cache postgresql-dev gcc openssl-dev libressl-dev musl-dev libffi-dev

ENV PYTHONUNBUFFERED 1

WORKDIR /django

COPY requirements.txt /django/requirements.txt
COPY tmp/secrets.json /django/tmp/secrets.json

RUN pip install --upgrade pip
RUN pip install wheel
RUN pip install gunicorn
RUN pip install --no-cache-dir -r requirements.txt

COPY . /django

RUN python manage.py collectstatic --noinput
RUN python manage.py migrate

EXPOSE 8080

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8080", "--timeout", "240"]