#!/bin/bash

set -x
set -e

git pull

docker build -t dog .

docker container rm --force dog_container || true

docker run --rm -it -p 5000:5000 --name dog_container dog
