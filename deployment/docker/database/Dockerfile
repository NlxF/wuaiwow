FROM wuaiwow/database:base

# Source code file
COPY ./deployment/config/backup.sh /usr/local/bin/backup.sh
COPY ./deployment/config/cronjobs /etc/cronjobs
COPY ./deployment/docker/database/docker-entrypoint.sh /docker-entrypoint-initdb.d

RUN ["chmod", "+x", "/usr/local/bin/backup.sh"]
RUN ["chmod", "+x", "/docker-entrypoint-initdb.d/docker-entrypoint.sh"]
RUN ["touch", "/var/log/cron.log"]

volume ./volume/backup:/www/wuaiwow-www/backup


