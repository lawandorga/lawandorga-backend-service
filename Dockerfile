FROM python:3.9

#RUN apk update && apk add --no-cache postgresql-dev gcc openssl-dev libressl-dev musl-dev libffi-dev

#ENV PYTHONUNBUFFERED 1

WORKDIR /django

COPY requirements.txt /django/requirements.txt
#COPY tmp/secrets.json /django/tmp/secrets.json

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

#RUN python production_manage.py collectstatic --noinput

COPY . /django

# collectstatic
ENV JWT_SIGNING_KEY=''
ENV FRONTEND_URL=''
RUN python manage.py collectstatic --noinput
# RUN python production_manage.py migrate

EXPOSE 8080

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8080", "--timeout", "240"]
