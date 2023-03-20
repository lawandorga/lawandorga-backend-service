FROM python:3.10

RUN adduser nonroot

RUN pip install --upgrade pip pipenv

RUN mkdir -p /django
RUN chown nonroot /django
WORKDIR /django

COPY --chown=nonroot:nonroot Pipfile /django/Pipfile
COPY --chown=nonroot:nonroot Pipfile.lock /django/Pipfile.lock

USER nonroot

RUN pipenv requirements > /django/requirements.txt
RUN pip install -r /django/requirements.txt

COPY --chown=nonroot:nonroot . /django

RUN python manage.py collectstatic --noinput

EXPOSE 8080

CMD ["gunicorn", "config.asgi:application", "--bind", "0.0.0.0:8080", "--timeout", "240", "-w", "4", "-k", "config.nonroots.Uvicornnonroot"]
