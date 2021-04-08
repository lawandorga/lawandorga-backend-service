chown -R root:www-data ./
chmod -R 750 ./
find ./ -type f -exec chmod 740 {} \;
chmod -R 770 ./tmp/media
find ./tmp/media -type f -exec chmod 760 {} \;
chmod 770 ./tmp/logs
chmod -R 760 ./tmp/logs/*
chmod 770 ./tmp
