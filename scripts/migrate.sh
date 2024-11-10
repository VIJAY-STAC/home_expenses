source /home/ubuntu/env/bin/activate >> deployment_log.txt 2>&1
cd /home/ubuntu/home_expenses >> deployment_log.txt 2>&1
cd home_expenses/ >> deployment_log.txt 2>&1
cp /home/ubuntu/.env . >> deployment_log.txt 2>&1

cd .. >> deployment_log.txt 2>&1
cp /home/ubuntu/db.sqlite3 . >> deployment_log.txt 2>&1

python manage.py makemigrations >> deployment_log.txt 2>&1
python manage.py migrate >> deployment_log.txt 2>&1

cd ../.. >> deployment_log.txt 2>&1
sudo rm -r .env >> deployment_log.txt 2>&1
sudo rm -r db.sqlite3 >> deployment_log.txt 2>&1

sudo service gunicorn restart >> deployment_log.txt 2>&1
sudo service nginx restart >> deployment_log.txt 2>&1
