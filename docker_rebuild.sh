#!/bin/bash

set -x
set -e

# git pull

docker build -t eu.gcr.io/magnetic-tenure-300523/dog80:latest .

docker container rm --force dog_container || true

docker run --rm -it -p 80:80 --name dog_container eu.gcr.io/magnetic-tenure-300523/dog80
