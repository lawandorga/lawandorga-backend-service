cd /home/law-orga-backend/ || exit
git reset --hard HEAD
git pull
tmp/venv/bin/pip install -r requirements.txt
tmp/venv/bin/python production_manage.py migrate
#tmp/venv/bin/python production_manage.py collectstatic --noinput
./permissions.sh
systemctl restart apache2
echo 'DEPLOYED'
