FROM python:3.9.6-alpine3.14

RUN mkdir -p /app

COPY ./src/ /app

WORKDIR /app

RUN pip3 install -r requirements.txt

ENV AWS_DEFAULT_REGION=us-east-2
