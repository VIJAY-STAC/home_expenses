#!/bin/bash

sed -i 's/\[]/\["65.0.222.195"]/' /home/ubuntu/home_expenses/home_expenses/settings.py
/home/ubuntu/env/bin/python manage.py makemigrations  
/home/ubuntu/env/bin/python manage.py migrate 
/home/ubuntu/env/bin/python manage.py collectstatic --noinput
sudo service gunicorn restart
sudo service nginx restart
