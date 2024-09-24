#!/bin/bash

exit # Exit right now because we don't have a repo set up and the docker image has secrets in the config file

tag="${1-latest}"

sudo DOCKER_BUILDKIT=1 docker build --cache-from mdcollins05/BlinkStickMQTT:${tag} --tag mdcollins05/BlinkStickMQTT:${tag} . && \
sudo docker push mdcollins05/BlinkStickMQTT:${tag}
