FROM python:3.9

WORKDIR /django

COPY requirements.txt /django/requirements.txt

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . /django

RUN python manage.py collectstatic --noinput

EXPOSE 8080

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8080", "--timeout", "240"]
