#!/bin/bash
source /home/ubuntu/env/bin/activate
cd /home/ubuntu/home_expenses 

# Set correct permissions for the project directory
sudo chown -R ubuntu:ubuntu /home/ubuntu/home_expenses
sudo chmod -R 775 /home/ubuntu/home_expenses 

# Copy .env file if it exists
cd home_expenses/
cp /home/ubuntu/.env . 

# Retain existing database file
cd ..
sudo cp /home/ubuntu/db.sqlite3 . 
sudo chmod 664 db.sqlite3 


# Run Django migrations
python manage.py makemigrations
python manage.py migrate 


# Clean up temporary .env (optional; remove only if necessary)

sudo rm home_expenses/.env &>> $LOG_FILE
sudo mv db.sqlite3 /home/ubuntu/


# Restart services
sudo service gunicorn restart
sudo service nginx restart 

