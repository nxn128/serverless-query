#!/bin/sh

# validate AWS creds are available in envars
if [[ -z "$AWS_ACCESS_KEY_ID" ]]; then
  echo "You must set the AWS_ACCESS_KEY_ID variable"
  exit 1
fi

if [[ -z "$AWS_SECRET_ACCESS_KEY" ]]; then
  echo "You must set the AWS_SECRET_ACCESS_KEY variable"
  exit 1
fi

# build infrastructure deployer image
docker build -t deployer -f deploy.Dockerfile .
# run deployer to roll out latest changes
docker run -t -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY deployer
