# TODO: remove this line after we fully support mysql 5.7
mysql -u root -p$MYSQL_ROOT_PASSWORD -e "SET GLOBAL sql_mode = '';"

# TODO: remove this line after we squash our DB updates
mysql -u root -p$MYSQL_ROOT_PASSWORD -e "SET GLOBAL max_allowed_packet=128*1024*1024;"

echo "Creating DB..."
mysql -u root -p$MYSQL_ROOT_PASSWORD -e "CREATE DATABASE IF NOT EXISTS wuaiwow"

#if [ -f ./thirdParty/thirdParty_build.sh ]; then
#    echo "Importing wuaiwow base..."
#    mysql -u root -p$MYSQL_ROOT_PASSWORD wuaiwow < /sql/wuaiwow_base.sql
#fi

#mysqldump -u root -p --add-drop-table --all-databases --force > data-for-upgrade.sql

crontab -u $(whoami) /etc/cronjobs
/etc/init.d/cron restart

echo "Done!"
