FROM python:3.10

RUN pip install --upgrade pip pipenv

RUN adduser -D worker
USER worker
WORKDIR /django

COPY --chown worker:worker Pipfile /django/Pipfile
COPY --chown worker:worker Pipfile.lock /django/Pipfile.lock

RUN pipenv requirements > requirements.txt
RUN pip install -r requirements.txt

COPY --chown worker:worker . /django

RUN python manage.py collectstatic --noinput

EXPOSE 8080

CMD ["gunicorn", "config.asgi:application", "--bind", "0.0.0.0:8080", "--timeout", "240", "-w", "4", "-k", "config.workers.UvicornWorker"]
