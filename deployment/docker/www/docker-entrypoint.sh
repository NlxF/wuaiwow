#!/bin/bash
set -e

HOME=/www/wuaiwow-www

echo "flask_cache compact for flask 1.0.2"
packages=($(python -c "import site; print(site.getsitepackages())" | tr -d "[],\'\'"))
for package in ${packages[@]}; do
    cache_path=${package}'/flask_cache/jinja2ext.py'
    echo 'search flask_cache at: '${cache_path}
    if [ -f ${cache_path} ]; then
        echo "find flask_cache"
        sed -i 's/^from flask.ext.cache /from flask_cache /g' ${cache_path}
        break
    fi
done

echo "Initialize DB..."
cd ${HOME}/
echo $(python manager.py db init)
echo $(python manager.py db migrate -m "init")
echo $(python manager.py db upgrade)

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