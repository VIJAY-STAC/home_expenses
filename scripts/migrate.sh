# Activate the virtual environment
source /home/ubuntu/env/bin/activate

# Navigate to the home_expenses directory
cd /home/ubuntu/home_expenses
cd home_expenses/

# Copy the environment file
cp /home/ubuntu/.env .

# Move to the parent directory and copy the database
cd ..
cp /home/ubuntu/db.sqlite3 .

# Fix permissions for db.sqlite3 to ensure Django can access it
sudo chmod 666 /home/ubuntu/db.sqlite3

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Return to the original directory and clean up sensitive files
cd ../..
sudo rm -r .env
sudo rm -r db.sqlite3

# Restart services to apply changes
sudo service gunicorn restart
sudo service nginx restart
