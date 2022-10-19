FROM python:3.9

WORKDIR /django

COPY Pipfile /django/Pipfile

RUN pip install --upgrade pip pipenv
RUN pipenv install --system

COPY . /django

RUN python manage.py collectstatic --noinput

EXPOSE 8080

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8080", "--timeout", "240"]
