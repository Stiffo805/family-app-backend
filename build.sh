#!/usr/bin/env bash

set -o errexit

pip install -r requirements.txt

cd family_app

python manage.py collectstatic --no-input

python manage.py migrate
