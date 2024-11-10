#!/usr/bin/env bash

virtualenv /home/ubuntu/env
source /home/ubuntu/env/bin/activate

pip install -r /home/ubuntu/home_expenses/requirements.txt
sudo apt-get install -y libpq-dev
pip install psycopg2
cd /home/ubuntu/env/bin
pip install gunicorn
cd ..//..//
cd home_expenses
cp /home/ubuntu/db.sqlite3 .
cd home_expenses/
cp /home/ubuntu/.env .
cd ..//..//
sudo rm -r .env
sudo rm -r db.sqlite3
