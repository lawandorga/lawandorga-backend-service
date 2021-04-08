git pull
tmp/venv/bin/pip install -r requirements.txt
tmp/venv/bin/python manage.py migrate
systemctl restart apache2
