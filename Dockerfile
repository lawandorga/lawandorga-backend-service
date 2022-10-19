FROM python:3.10

WORKDIR /django

COPY Pipfile /django/Pipfile
COPY Pipfile.lock /django/Pipfile.lock

RUN pip install --upgrade pip pipenv
RUN pipenv requirements > requirements.txt
RUN pip install -r requirements.txt

COPY . /django

RUN python manage.py collectstatic --noinput

EXPOSE 8080

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8080", "--timeout", "240"]
