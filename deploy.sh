git reset --hard HEAD
git pull
tmp/venv/bin/pip install -r requirements.txt
tmp/venv/bin/python manage.py migrate
tmp/venv/bin/python manage.py collectstatic --noinput
./permissions.sh
systemctl restart apache2
