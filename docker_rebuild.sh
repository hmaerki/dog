#!/bin/bash

set -x
set -e

# git pull

docker build -t dog .

docker container rm --force dog_container || true

docker run --rm -it -p 80:80 --name dog_container dog
