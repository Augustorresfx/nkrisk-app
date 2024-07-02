#!/usr/bin/env bash
# exit on error
set -o errexit

RUN apt-get update && apt-get install -y \
    libpango-1.0-0 \
    libcairo2 \
    libgdk-pixbuf2.0-0 \
    && rm -rf /var/lib/apt/lists/*
    
# poetry install 
pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py makemigrations
python manage.py migrate
#if [[ $CREATE_SUPERUSER ]];
#then
#  python manage.py createsuperuser --no-input
#fi

