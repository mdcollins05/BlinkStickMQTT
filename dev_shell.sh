#!/bin/bash

sudo docker run -it --rm --volume $(pwd):/app --workdir /app --privileged python:3.9-slim /bin/bash

