import os
import time
import getpass    # getpass.getuser()   whoami
import requests
import http.cookiejar as cookiejar
from datetime import datetime
from pathlib import Path as _Path
from datetime import datetime as _datetime
from fabric import network
from fabric.api import *
from fabric.utils import abort
from fabric.contrib.files import exists


"""local()和run()，分别在本地和远程执行命令，put()可以把本地文件上传到远程，
当需要在远程指定当前目录时，只需用with cd('/path/to/dir/'):即可。
默认情况下，当命令执行失败时，Fabric会停止执行后续命令。
有时，我们允许忽略失败的命令继续执行，比如run('rm /tmp/abc')在文件不存在的时候有可能失败，
这时可以用with settings(warn_only=True):执行命令，这样Fabric只会打出警告信息而不会中断执行
"""

# ----- supervisor认证 ----- #
USERNAME = 'luxf'
PASSWORD = 'lxf'

_DB_USER  = 'root'
_DB_PSWD  = 'lxf.3517'
_DB_NAME  = 'banyg360'

SSH_NEW_PORT = 22  # 50683                        # rule.v4中开放的端口需跟此一致

# -------- fab设置 -------- #
# env.hosts = ['192.168.1.19:%d' % SSH_NEW_PORT]           # 如果有多个主机，fabric会自动依次部署
# env.user = 'luxf'
env.hosts = ['206.189.216.83:%d' % SSH_NEW_PORT]          # 如果有多个主机，fabric会自动依次部署
env.user = 'root'
env.use_ssh_config = True
env.key_filename = ['~/.ssh/ism_rsa']


_REMOTE_DIR     = '/www'
_REMOTE_DIR_APP = '/www/app'
_TAR_DIR_NAME   = 'wuaiwow'
_TAR_FILE_TEMP  = '{}.tar.gz@{}'
_TAR_FILE_NAME  = None
_PACKAGE_DIR    = 'package/'
_BACKUP_DIR     = 'backup'

VHOST = _TAR_DIR_NAME
REDIS = 'redis-server'

FIRST_RUN = True


def _start_webserver():
    """启动 Nginx"""
    sudo("service nginx start")


def _reload_webserver():
    """重启 Nginx"""
    sudo("service nginx reload")


def _stop_webserver():
    """停止 Nginx"""
    sudo("service nginx stop")


def _start_app():
    """开启uwsgi服务器"""
    # sudo('supervisorctl -u %s -p %s reload' % (USERNAME, PASSWORD))
    # sudo('supervisorctl -u %s -p %s start %s' % (USERNAME, PASSWORD, VHOST))
    sudo('supervisorctl reload')
    sudo('supervisorctl start %s' % VHOST)


def _reload_app(touch=True):
    """重启uwsgi服务器"""
    # sudo('supervisorctl -u %s -p %s reload' % (USERNAME, PASSWORD))
    # sudo('supervisorctl -u %s -p %s restart %s' % (USERNAME, PASSWORD, VHOST))
    sudo('supervisorctl reload')
    sudo('supervisorctl restart %s' % VHOST)


def _stop_app():
    """暂停uwsgi服务器"""
    # sudo('supervisorctl -u %s -p %s stop %s' % (USERNAME, PASSWORD, VHOST))
    sudo('supervisorctl stop %s' % VHOST)


def _start_redis():
    """启动redis服务器"""
    # sudo('supervisorctl -u %s -p %s start %s' % (USERNAME, PASSWORD, REDIS))
    sudo('supervisorctl start %s' % REDIS)


def _stop_redis():
    """停止redis服务器"""
    # sudo('supervisorctl -u %s -p %s stop %s' % (USERNAME, PASSWORD, REDIS))
    sudo('supervisorctl stop %s' % REDIS)


def _make_package(file_name):
    """定义一个打包任务, 指定包名"""
    tar_files = ['bwg360/*', 'config/*', 'cookies.txt', 'requirements.txt', '*.py', 'maintain.html']
    exclude_file = ['', '*.tar.gz', 'fabfile.py', '.idea', 'doc', 'envwin', 'envlinux', 'envmacos', 'migrations',
                    'pic', 'src', 'package', '*.crx', '*.rdb', '*.db', '__pycache__', 'test', '.DS_Store']
    exclude_cmd = ' --exclude='.join(exclude_file)
    local('rm -f {}{}'.format(_PACKAGE_DIR, file_name))
    local('tar -czvf {}{} {} {}'.format(_PACKAGE_DIR, file_name, exclude_cmd, ' '.join(tar_files)))


def _update_repo_env():

    with cd(_REMOTE_DIR_APP):

        # 激活 env
        sudo('source venv/bin/activate')
        sudo('pip3 install --upgrade pip')

        # 更新依赖库
        sudo('venv/bin/python3 -m pip install -r {}/requirements.txt'.format(_TAR_DIR_NAME))
        sudo('venv/bin/python3 -m pip install mysql-connector-python')

        # Python lib path
        with cd('venv/lib'):
            lib_path = run('ls | grep python3')
            full_lib_path = "{}/venv/lib/{}/site-packages".format(_REMOTE_DIR_APP, lib_path)
            flask_cache_path = "{}/flask_cache/jinja2ext.py".format(full_lib_path)
            if exists('{}/site-packages/flask_cache/jinja2ext.py'.format(lib_path)):
                sudo("sed -i 's/^from flask.ext.cache /from flask_cache /g' {}".format(flask_cache_path))

            flask_migrate_path = "{}/flask_migrate/templates/script.py.mako".format(full_lib_path)
            if exists('{}/site-packages/flask_migrate/templates/script.py.mako'.format(lib_path)):
                sudo("sed -i 's/^import sqlalchemy as sa /import sqlalchemy as sa \\\n import bwg360 /g' {}".format(flask_migrate_path))

        with cd(_TAR_DIR_NAME):
            # 拷贝
            if exists('/etc/nginx/sites-available/banyg360_maintain'):
                sudo('rm -f /etc/nginx/sites-available/banyg360_maintain')
            sudo('cp config/banyg360_maintain /etc/nginx/sites-available/banyg360_maintain')

            if exists('/etc/nginx/sites-available/banyg360_normal'):
                sudo('rm -f /etc/nginx/sites-available/banyg360_normal')
            sudo('cp config/banyg360_normal /etc/nginx/sites-available/banyg360_normal')

            all_supervisor_conf = ['banyg360_supervisor.conf', 'redis_supervisor.conf']
            for conf in all_supervisor_conf:
                if exists('/etc/supervisor/conf.d/{}'.format(conf)):
                    sudo('rm -f /etc/supervisor/conf.d/{}'.format(conf))
                sudo('cp config/{0} /etc/supervisor/conf.d/{0}'.format(conf))

            # if exists('/etc/supervisor/conf.d/banyg360_supervisor.conf'):
            #     sudo('rm -f /etc/supervisor/conf.d/banyg360_supervisor.conf')
            # sudo('cp config/banyg360_supervisor.conf /etc/supervisor/conf.d/banyg360_supervisor.conf')
            #
            # if exists('/etc/supervisor/conf.d/redis_supervisor.conf'):
            #     sudo('rm -f /etc/supervisor/conf.d/redis_supervisor.conf')
            # sudo('cp config/redis_supervisor.conf /etc/supervisor/conf.d/redis_supervisor.conf')
            #
            # if exists('/etc/supervisor/conf.d/redis_supervisor.conf'):
            #     sudo('rm -f /etc/supervisor/conf.d/redis_supervisor.conf')
            # sudo('cp config/redis_supervisor.conf /etc/supervisor/conf.d/redis_supervisor.conf')

            # sudo('supervisorctl -u %s -p %s reload' % (USERNAME, PASSWORD))
            # sudo('supervisorctl reload')

            if not exists('/var/run/supervisor.sock'):
                sudo('touch /var/run/supervisor.sock')
                sudo('chmod 777 /var/run/supervisor.sock')
                sudo('supervisord -c /etc/supervisor/supervisord.conf')

            # 第一次执行
            if FIRST_RUN:
                # flask_user的翻译
                translations_zh_path = "{}/flask_user/translations/zh/LC_MESSAGES".format(full_lib_path)
                if exists("{}/flask_user.po".format(translations_zh_path)):
                    sudo('rm -f {}/flask_user.po'.format(translations_zh_path))
                    sudo('rm -f {}/flask_user.mo'.format(translations_zh_path))
                    sudo('cp config/translations/zh/LC_MESSAGES/flask_user.po {}'.format(translations_zh_path))
                    sudo('cp config/translations/zh/LC_MESSAGES/flask_user.mo {}'.format(translations_zh_path))


def _upload_repo(tag=None):
    """上传指定版本的package,tag格式'xxxxxxxx(20180807)' """
    global _TAR_FILE_NAME
    if not tag:
        tag = _datetime.now().strftime('%Y%m%d')
        _TAR_FILE_NAME = _TAR_FILE_TEMP.format(_TAR_DIR_NAME, tag)

        _make_package(_TAR_FILE_NAME)
    else:
        _TAR_FILE_NAME = _TAR_FILE_TEMP.format(_TAR_DIR_NAME, tag)

        file = _Path(_PACKAGE_DIR + _TAR_FILE_NAME)
        if not file.exists():
            abort('Specified tag does not exist!!!')

    # local('rsync -avz . {}:{} --delete --exclude-from \'rsync_exclude.txt\''.format(host, _REMOTE_DIR_APP))
    put('%s/%s' % (_PACKAGE_DIR, _TAR_FILE_NAME), _REMOTE_DIR_APP, use_sudo=True)

    with cd(_REMOTE_DIR_APP):
        remote_dist_link = "{}/{}".format(_REMOTE_DIR_APP, _TAR_DIR_NAME)
        remote_dist_dir = "{}/{}{}".format(_REMOTE_DIR_APP, _TAR_DIR_NAME, tag)

        # 先备份migrations
        if exists(remote_dist_link) and exists("{}/migrations".format(remote_dist_link)):
            with cd(remote_dist_link):
                sudo('mv migrations ../')

        # 解压
        if not exists(remote_dist_dir):
            sudo('mkdir %s' % remote_dist_dir)
        sudo('tar -zxvf %s -C %s' % (_TAR_FILE_NAME, remote_dist_dir))
        sudo('rm -f %s' % _TAR_FILE_NAME)
        # 设定新目录的www-data权限
        sudo('chown -R www-data:www-data {}'.format(remote_dist_dir))
        # 删除旧的软连接
        sudo('rm -f {}/{}'.format(_REMOTE_DIR_APP, _TAR_DIR_NAME))
        # 创建新的软连接指向新部署的目录
        sudo('ln -s %s %s' % (remote_dist_dir, remote_dist_link))
        sudo('chown -R www-data:www-data %s' % remote_dist_link)

        # migrations移入新的工作目录
        if exists("{}/migrations".format(_REMOTE_DIR_APP)):
            sudo('mv migrations {}'.format(remote_dist_dir))

    _update_repo_env()


def _enable_nginx_normal_config():
    if exists('/etc/nginx/sites-enabled/default'):
        sudo('rm -f /etc/nginx/sites-enabled/default')
    if exists('/etc/nginx/sites-enabled/banyg360_maintain'):
        sudo('rm -f /etc/nginx/sites-enabled/banyg360_maintain')

    if not exists('/etc/nginx/sites-enabled/banyg360_normal'):
        if exists('/etc/nginx/sites-available/banyg360_normal'):
            sudo('ln -s /etc/nginx/sites-available/banyg360_normal /etc/nginx/sites-enabled/banyg360_normal')
        else:
            abort('normal config not exist')

    if not exists('{}/normal_access.log'.format(_REMOTE_DIR_APP)):
        sudo('touch %s/normal_access.log' % _REMOTE_DIR_APP)
        sudo('chown -R www-data:www-data %s/normal_access.log' % _REMOTE_DIR_APP)
    if not exists('{}/normal_error.log'.format(_REMOTE_DIR_APP)):
        sudo('touch %s/normal_error.log' % _REMOTE_DIR_APP)
        sudo('chown -R www-data:www-data %s/normal_error.log' % _REMOTE_DIR_APP)


def _enable_nginx_maintain_config():
    if exists('/etc/nginx/sites-enabled/default'):
        sudo('rm -f /etc/nginx/sites-enabled/default')
    if exists('/etc/nginx/sites-enabled/banyg360_normal'):
        sudo('rm -f /etc/nginx/sites-enabled/banyg360_normal')

    if not exists('/etc/nginx/sites-enabled/banyg360_maintain'):
        if exists('/etc/nginx/sites-available/banyg360_maintain'):
            sudo('ln -s /etc/nginx/sites-available/banyg360_maintain /etc/nginx/sites-enabled/banyg360_maintain')
        else:
            abort('maintain config not exist')

    if not exists('{}/maintain_access.log'.format(_REMOTE_DIR_APP)):
        sudo('touch %s/maintain_access.log' % _REMOTE_DIR_APP)
        sudo('chown -R www-data:www-data %s/maintain_access.log' % _REMOTE_DIR_APP)
    if not exists('{}/maintain_error.log'.format(_REMOTE_DIR_APP)):
        sudo('touch %s/maintain_error.log' % _REMOTE_DIR_APP)
        sudo('chown -R www-data:www-data %s/maintain_error.log' % _REMOTE_DIR_APP)


def _prepare():
    """更新运行环境"""
    # set timezone UTC
    sudo('timedatectl set-timezone UTC')
    sudo('service cron restart')


def _ssh_setting():
    """ssh 设置"""

    if exists("/etc/ssh/sshd_config"):
        sudo("sed -i 's/^Port .*/Port {}/g' /etc/ssh/sshd_config".format(SSH_NEW_PORT))
        sudo("/etc/init.d/ssh restart")

    network.disconnect_all()


def _get_backup_to_local():
    """最新数据备份到本地"""
    out_put = run('ls %s/%s' % (_REMOTE_DIR_APP, _BACKUP_DIR))
    back_files = out_put.split()
    for file_name in back_files:
        tag = str(datetime.utcnow().strftime("%Y-%m-%d"))
        if tag in file_name:
            get("{}/{}/{}".format(_REMOTE_DIR_APP, _BACKUP_DIR, file_name), "%s/" % _BACKUP_DIR, use_sudo=True)


def _security_setting():
    """服务器安全设置"""
    # fail2ban
    sudo('apt-get install fail2ban -y')

    if exists("/etc/fail2ban/jail.conf"):
        # backup
        sudo('service fail2ban stop')
        with cd(os.path.join(_REMOTE_DIR_APP, _TAR_DIR_NAME)):
            put('config/jail.local', '/etc/fail2ban/', use_sudo=True)

        sudo('service fail2ban start')

    # iptables setting
    sudo('apt-get install iptables-persistent -y')

    with cd(os.path.join(_REMOTE_DIR_APP, _TAR_DIR_NAME)):
        put('config/rules.v4', '/etc/iptables/', use_sudo=True)
        # put('config/rules.v6', '/etc/iptables/', use_sudo=True)    # 不更新，会阻塞DNS查询

    try:
        sudo('sudo service netfilter-persistent reload')
    except:
        pass
        # sudo('sudo service iptables-persistent reload')


def _first_run(first):
    global FIRST_RUN
    FIRST_RUN = first


def init_env():
    """第一次运行时初始化环境"""

    # try:
    #     execute(_ssh_setting, hosts=[h.replace(str(SSH_NEW_PORT), '22') for h in env.hosts])
    # except:
    #     pass

    _prepare()

    if not exists(_REMOTE_DIR):
        sudo('mkdir {} {}'.format(_REMOTE_DIR, _REMOTE_DIR_APP))

    with cd(_REMOTE_DIR_APP):
        if not exists('venv'):
            sudo('virtualenv --python=python3 venv')

    _security_setting()


def init_repo_task():
    """定义一个初始化repo任务"""
    for host in env.hosts:

        # _stop_webserver()
        # _stop_app()
        # _stop_redis()

        # 只有第一次运行才为True
        _first_run(True)
        _upload_repo()

        _start_redis()
        _start_app()
        _enable_nginx_normal_config()
        # _start_webserver()
        _reload_webserver()


def update_repo_task():
    """定义一个repo更新任务"""
    for host in env.hosts:
        _enable_nginx_maintain_config()
        _reload_webserver()
        _stop_app()
        # _stop_redis()

        _first_run(False)
        tag = None                      # 可以指定上传的tag
        _upload_repo(tag=tag)

        # _start_redis()
        _reload_app()
        _enable_nginx_normal_config()
        _reload_webserver()


