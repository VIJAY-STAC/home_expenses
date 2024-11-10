#!/bin/bash
LOG_FILE="/home/ubuntu/deployment.log"

log() {
  echo "$1" | tee -a $LOG_FILE
}

# Activate virtual environment
log "Activating virtual environment..."
source /home/ubuntu/env/bin/activate

# Change to project directory
log "Changing to project directory..."
cd /home/ubuntu/home_expenses || { log "Failed to change directory"; exit 1; }

# Set correct permissions for the project directory
log "Setting permissions for project directory..."
sudo chown -R ubuntu:ubuntu /home/ubuntu/home_expenses &>> $LOG_FILE
chmod 775 /home/ubuntu/home_expenses &>> $LOG_FILE

# Copy .env file if it exists
log "Copying .env file..."
cd home_expenses/
if [ -f "/home/ubuntu/.env" ]; then
  cp /home/ubuntu/.env . &>> $LOG_FILE
else
  log ".env file not found, skipping copy."
fi

# Retain existing database file
log "Ensuring db.sqlite3 is retained..."
cd ..
if [ ! -f "db.sqlite3" ]; then
  if [ -f "/home/ubuntu/db.sqlite3" ]; then
    log "Copying existing db.sqlite3 from /home/ubuntu..."
    sudo cp /home/ubuntu/db.sqlite3 . &>> $LOG_FILE
    sudo chmod 664 db.sqlite3 &>> $LOG_FILE
    log "Existing db.sqlite3 copied and permissions set."
  else
    log "db.sqlite3 not found in /home/ubuntu, no database copied."
  fi
else
  log "Existing db.sqlite3 found, skipping copy to retain data."
fi

# Run Django migrations
log "Running makemigrations..."
python manage.py makemigrations &>> $LOG_FILE
if [ $? -eq 0 ]; then
  log "Makemigrations successful"
else
  log "Makemigrations failed"
fi

log "Running migrate..."
python manage.py migrate &>> $LOG_FILE
if [ $? -eq 0 ]; then
  log "Migrate successful"
else
  log "Migrate failed"
fi

# Clean up temporary .env (optional; remove only if necessary)
log "Cleaning up temporary .env and db.sqlite3 (if needed)..."
if [ -f "home_expenses/.env" ]; then
  sudo rm home_expenses/.env &>> $LOG_FILE
fi
if [ -f "db.sqlite3" ] && [ ! -f "/home/ubuntu/db.sqlite3" ]; then
  sudo mv db.sqlite3 /home/ubuntu/ &>> $LOG_FILE
fi

# Restart services
log "Restarting gunicorn..."
sudo service gunicorn restart &>> $LOG_FILE
if [ $? -eq 0 ]; then
  log "Gunicorn restarted successfully"
else
  log "Gunicorn restart failed"
fi

log "Restarting nginx..."
sudo service nginx restart &>> $LOG_FILE
if [ $? -eq 0 ]; then
  log "Nginx restarted successfully"
else
  log "Nginx restart failed"
fi

log "Deployment script completed."
