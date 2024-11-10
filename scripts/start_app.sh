#!/usr/bin/bash 

sed -i 's/\[]/\["65.0.222.195"]/' /home/ubuntu/home_expenses/home_expenses/settings.py
python manage.py makemigrations  
python manage.py migrate 
python manage.py collectstatic
sudo service gunicorn restart
sudo service nginx restart
#sudo tail -f /var/log/nginx/error.log
#sudo systemctl reload nginx
#sudo tail -f /var/log/nginx/error.log
#sudo nginx -t
#sudo systemctl restart gunicorn
#sudo systemctl status gunicorn
#sudo systemctl status nginx
# Check the status
#systemctl status gunicorn
# Restart:
#systemctl restart gunicorn
#sudo systemctl status nginx
