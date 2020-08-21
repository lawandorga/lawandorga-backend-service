FROM python:3.6.12-alpine3.12


#RUN apk update \
#    && apk add -y --no-install-recommends \
#        postgresql-client \
#    && rm -rf /var/lib/apt/lists/*
RUN apk add --no-cache --virtual .build-deps \
    ca-certificates gcc postgresql-dev linux-headers musl-dev \
    libffi-dev jpeg-dev zlib-dev
RUN pip install --upgrade pip

WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . .

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
