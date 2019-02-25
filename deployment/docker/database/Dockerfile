FROM wuaiwow/database:base

# Source code file
COPY ./deployment/config/backup.sh /usr/local/bin/backup.sh
COPY ./deployment/docker/database/docker-entrypoint.sh /docker-entrypoint-initdb.d

# COPY ./deployment/config/cronjobs /var/spool/cron/crontabs/root
# RUN chmod 0644 /var/spool/cron/crontabs/root
COPY ./deployment/config/cronjobs /etc/cron.d/cronjobs
RUN chmod 0644 /etc/cron.d/cronjobs && crontab /etc/cron.d/cronjobs
RUN touch /var/run/crond.pid && chmod +x /var/run/crond.pid

RUN usermod -a -G root mysql 
# RUN chown mysql:root /var/run/crond.pid && \
#     chown mysql:root /usr/sbin/cron && \
#     chmod u+s /usr/bin/crontab
RUN chown root:root /usr/bin/crontab
RUN chmod u+s /usr/bin/crontab

RUN ["chmod", "+x", "/usr/local/bin/backup.sh"]
RUN ["chmod", "+x", "/docker-entrypoint-initdb.d/docker-entrypoint.sh"]
RUN ["touch", "/var/log/cron.log"]

VOLUME ./volume/backup:/www/wuaiwow-www/backup
# VOLUME ./database/:/docker-entrypoint-initdb.d/schema.sql:ro