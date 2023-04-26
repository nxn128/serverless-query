FROM python:3.9.6-alpine3.14

RUN apk update && \
  apk upgrade && \
  apk add bash && \
  apk add --no-cache --virtual build-deps build-base gcc libffi-dev && \
  pip3 install awscliv2 && \
  pip3 install aws-sam-cli && \
  mkdir -p /code

COPY ./ /code

WORKDIR /code

ENV AWS_DEFAULT_REGION=us-east-2

CMD sam build && sam deploy
