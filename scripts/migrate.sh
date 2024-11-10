#!/bin/bash
source /home/ubuntu/env/bin/activate
cd /home/ubuntu/home_expenses

cp /home/ubuntu/db.sqlite3 .
chmod 664 db.sqlite3
sudo chown -R ubuntu:ubuntu /home/ubuntu/home_expenses
chmod 775 /home/ubuntu/home_expenses
cd home_expenses/
cp /home/ubuntu/.env .
cd ..//..//
sudo rm -r .env
sudo rm -r db.sqlite3

python manage.py makemigrations
python manage.py migrate
sudo service gunicorn restart 
sudo service nginx restart


