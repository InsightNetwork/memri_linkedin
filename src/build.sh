#!/bin/bash
docker build --tag memri_linkedin/plugin:1.0 --build-arg VIS_OWNER_KEY=$VIS_OWNER_KEY --build-arg VIS_DATABASE_KEY=$VIS_DATABASE_KEY .