#!/bin/bash

LOGFILE="/home/ubuntu/deployment.log"
echo "Starting migration process..." >> $LOGFILE
sed -i 's/\[]/\["65.0.222.195"]/' /home/ubuntu/home_expenses/home_expenses/settings.py >> $LOGFILE 2>&1
/home/ubuntu/env/bin/python manage.py makemigrations >> $LOGFILE 2>&1
/home/ubuntu/env/bin/python manage.py migrate >> $LOGFILE 2>&1
/home/ubuntu/env/bin/python manage.py collectstatic --noinput >> $LOGFILE 2>&1
sudo service gunicorn restart >> $LOGFILE 2>&1
sudo service nginx restart >> $LOGFILE 2>&1
echo "Migration process completed." >> $LOGFILE
