#!/bin/bash
source /home/ubuntu/env/bin/activate
cd /home/ubuntu/home_expenses
python manage.py makemigrations
python manage.py migrate

sudo service gunicorn restart 
sudo service nginx restart