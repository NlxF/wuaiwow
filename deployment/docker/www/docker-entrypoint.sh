#!/bin/bash
set -e

HOME=/www/wuaiwow-www

echo "init db..."
python ${HOME}/manager.py db init
python ${HOME}/manager.py db migrate -m "initdb"
python ${HOME}/manager.py db upgrade


echo "start supervisord..."
# if the running user is an Arbitrary User ID
if ! whoami &> /dev/null; then
    # make sure we have read/write access to /etc/passwd
    if [ -w /etc/passwd ]; then
        # write a line in /etc/passwd for the Arbitrary User ID in the 'root' group
        echo "${USER_NAME:-default}:x:$(id -u):0:${USER_NAME:-default} user:${HOME}:/sbin/nologin" >> /etc/passwd
    fi
fi
if [ "$1" = 'supervisord' ]; then
    exec /usr/bin/supervisord
fi

exec "$@"