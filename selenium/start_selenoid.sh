#!/bin/bash

mkdir -p ~/data/selenoid

cp browsers.json ~/data/selenoid

docker pull selenoid/chrome:latest
docker pull selenoid/firefox:46.0

docker run -d                                       \
    --name selenoid                                 \
    -p 4444:4444                                    \
    -v /var/run/docker.sock:/var/run/docker.sock    \
    -v ~/data/selenoid/:/etc/selenoid/:ro    \
    aerokube/selenoid:latest-release