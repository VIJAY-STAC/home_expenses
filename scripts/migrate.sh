#!/bin/bash
LOG_FILE="/home/ubuntu/deployment.log"

# Activate virtual environment
echo "Activating virtual environment..." | tee -a $LOG_FILE
source /home/ubuntu/env/bin/activate

# Change to project directory
echo "Changing to project directory..." | tee -a $LOG_FILE
cd /home/ubuntu/home_expenses || exit

# Run Django migrations
echo "Running makemigrations..." | tee -a $LOG_FILE
python manage.py makemigrations &>> $LOG_FILE
if [ $? -eq 0 ]; then
  echo "Makemigrations successful" | tee -a $LOG_FILE
else
  echo "Makemigrations failed" | tee -a $LOG_FILE
fi

echo "Running migrate..." | tee -a $LOG_FILE
python manage.py migrate &>> $LOG_FILE
if [ $? -eq 0 ]; then
  echo "Migrate successful" | tee -a $LOG_FILE
else
  echo "Migrate failed" | tee -a $LOG_FILE
fi

# Database operations
echo "Replacing db.sqlite3..." | tee -a $LOG_FILE
sudo rm -rf db.sqlite3 &>> $LOG_FILE
cp /home/ubuntu/db.sqlite3 . &>> $LOG_FILE
chmod 664 db.sqlite3 &>> $LOG_FILE
sudo chown -R ubuntu:ubuntu /home/ubuntu/home_expenses &>> $LOG_FILE
chmod 775 /home/ubuntu/home_expenses &>> $LOG_FILE

# Copy environment file
echo "Copying .env file..." | tee -a $LOG_FILE
cd home_expenses/ || exit
cp /home/ubuntu/.env . &>> $LOG_FILE
cd ../../ || exit
sudo rm -r .env &>> $LOG_FILE
sudo rm -r db.sqlite3 &>> $LOG_FILE

# Restart services
echo "Restarting gunicorn..." | tee -a $LOG_FILE
sudo service gunicorn restart &>> $LOG_FILE
if [ $? -eq 0 ]; then
  echo "Gunicorn restarted successfully" | tee -a $LOG_FILE
else
  echo "Gunicorn restart failed" | tee -a $LOG_FILE
fi

echo "Restarting nginx..." | tee -a $LOG_FILE
sudo service nginx restart &>> $LOG_FILE
if [ $? -eq 0 ]; then
  echo "Nginx restarted successfully" | tee -a $LOG_FILE
else
  echo "Nginx restart failed" | tee -a $LOG_FILE
fi

echo "Deployment script completed." | tee -a $LOG_FILE
