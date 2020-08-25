###
# BUIDLER
###
FROM python:3.6.12-alpine3.12 as builder

WORKDIR /usr/src/app
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev \
    ca-certificates gcc postgresql-dev linux-headers \
    libffi-dev jpeg-dev zlib-dev
RUN pip install --upgrade pip
COPY . .
COPY requirements.txt ./
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt




#########
# FINAL #
#########

# pull official base image
FROM python:3.6.12-alpine3.12

# create directory for the app user
RUN mkdir -p /home/app

# create the app user
RUN addgroup -S app && adduser -S app -G app

# create the appropriate directories
ENV HOME=/home/app
ENV APP_HOME=/home/app/web
RUN mkdir $APP_HOME
WORKDIR $APP_HOME

# install dependencies
RUN apk update && apk add libpq postgresql-dev gcc python3-dev musl-dev

COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .
RUN pip install --no-cache /wheels/*

# copy project
COPY . $APP_HOME

# chown all the files to the app user
RUN chown -R app:app $APP_HOME

# change to the app user
USER app

#CMD ["gunicorn", "backend.wsgi:application", "--bind", "0.0.0.0:8000"]



#FROM python:3.6.12-alpine3.12
#
#RUN apk add --no-cache --virtual .build-deps \
#    ca-certificates gcc postgresql-dev linux-headers musl-dev \
#    libffi-dev jpeg-dev zlib-dev
#RUN pip install --upgrade pip
#
#
#WORKDIR /usr/src/app
#RUN addgroup -S app && adduser -S app -G app
#
#ENV HOME=/usr/src
#ENV APP_HOME=/usr/src/app
#
#COPY requirements.txt ./
#RUN pip install -r requirements.txt
#COPY . .
#
#RUN chown -R app:app $APP_HOME
#
#EXPOSE 8000
#
#USER app
#
#CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
