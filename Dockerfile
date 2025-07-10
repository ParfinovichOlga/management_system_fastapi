FROM python:3.9-alpine3.13

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED=1

COPY ./requirements.txt /tmp/requirements.txt

COPY ./app /app

WORKDIR /app


RUN pip install --upgrade pip &&\
    pip install -r /tmp/requirements.txt

