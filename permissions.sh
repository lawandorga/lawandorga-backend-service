chown -R root:www-data /home/law-orga-backend
chmod -R 750 /home/law-orga-backend
find /home/law-orga-backend -type f -print0|xargs -0 chmod 740
chmod -R 770 /home/law-orga-backend/tmp/media
find /home/law-orga-backend/tmp/media -type f -print0|xargs -0 chmod 760
chmod 770 /home/law-orga-backend/tmp/logs
chmod -R 760 /home/law-orga-backend/tmp/logs/*
chmod 770 /home/law-orga-backend/tmp
