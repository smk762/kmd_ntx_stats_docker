#!/bin/bash
set -x
./fetch-params.sh
./configure.py
docker compose stop
git pull
docker compose build
docker compose run web python3 manage.py migrate
docker compose run web python3 manage.py makemigrations 
docker compose up -d
docker compose logs -f --tail=100
# TODO: include nginx / ssl
# TODO: crontab entries