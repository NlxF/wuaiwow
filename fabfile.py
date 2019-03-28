#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
# import time
# import getpass    # getpass.getuser()   whoami
# import http.cookiejar as cookiejar
from datetime import datetime as _datetime
from fabric import network
from fabric.api import *
# from fabric.utils import abort
from fabric.contrib.files import exists


"""local()和run()，分别在本地和远程执行命令，put()可以把本地文件上传到远程，
当需要在远程指定当前目录时，只需用with cd('/path/to/dir/'):即可。
默认情况下，当命令执行失败时，Fabric会停止执行后续命令。
有时，我们允许忽略失败的命令继续执行，比如run('rm /tmp/abc')在文件不存在的时候有可能失败，
这时可以用with settings(warn_only=True):执行命令，这样Fabric只会打出警告信息而不会中断执行
"""

# -------- fab设置 -------- #
SSH_NEW_PORT = 22  # 50683                               # rule.v4中开放的端口需跟此一致
env.hosts = ['10.49.192.82:%d' % SSH_NEW_PORT]           # 如果有多个主机，fabric会自动依次部署
env.user = 'luxf'
# env.hosts = ['206.189.216.83:%d' % SSH_NEW_PORT]           # 如果有多个主机，fabric会自动依次部署
# env.user = 'root'
# env.use_ssh_config = True
# env.key_filename = ['~/.ssh/wuaiwow_rsa']

_REMOTE_DIR     = '/www'
_TAR_DIR_NAME   = 'wuaiwow'
_REMOTE_DIR_APP = os.path.join(_REMOTE_DIR, _TAR_DIR_NAME)  # '/www/app'
_TAR_FILE_TEMP  = '{}.tar.gz@{}'
_BACKUP_DIR     = 'volume/backup'
_PACKAGE_DIR    = 'package/'


def _prepare():
    """更新运行环境"""
    # set timezone UTC
    sudo('timedatectl set-timezone "Asia/Shanghai"')

    sudo('apt-get update')
    sudo('apt-get install -y apt-transport-https ca-certificates curl gnupg-agent software-properties-common python-pip')

    # add the GPG key for the official Docker repository to system
    sudo('curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -')
    # add the Docker repository to APT sources:
    sudo('add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"')
    # update the package database with the Docker packages
    sudo('apt-get update')
    # make sure we are about to install from the Docker repo instead of the default Ubuntu repo
    sudo('apt-cache policy docker-ce')
    # Finally, install Docker
    sudo('apt-get install -y docker-ce')

    # executing the Docker Command Without Sudo
    # add your username to the docker group
    sudo('usermod -aG docker ${USER}')
    # apply the new group membership
    # sudo('su - ${USER}')

    # download the current stable release of Docker Compose
    # sudo('pip install docker-compose')
    if not exists('/usr/local/bin/docker-compose'):
        sudo('curl -L "https://github.com/docker/compose/releases/download/1.23.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose')
        sudo('chmod +x /usr/local/bin/docker-compose')
        sudo('ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose')

    sudo('docker login')


def _ssh_setting():
    """ssh 设置"""

    if exists("/etc/ssh/sshd_config"):
        sudo("sed -i 's/^Port .*/Port {}/g' /etc/ssh/sshd_config".format(SSH_NEW_PORT))
        sudo("/etc/init.d/ssh restart")

    network.disconnect_all()


def _security_setting():
    """服务器安全设置"""
    # fail2ban
    sudo('apt-get install fail2ban -y')

    if exists("/etc/fail2ban/jail.conf"):
        # backup
        sudo('service fail2ban stop')
        with cd(_REMOTE_DIR_APP):
            put('deployment/config/jail.local', '/etc/fail2ban/', use_sudo=True)

        sudo('service fail2ban start')

    # iptables setting
    sudo('apt-get install iptables-persistent -y')

    with cd(_REMOTE_DIR_APP):
        put('deployment/config/rules.v4', '/etc/iptables/', use_sudo=True)
        # put('deployment/config/rules.v6', '/etc/iptables/', use_sudo=True)    # 不更新，会阻塞DNS查询

    try:
        sudo('sudo service netfilter-persistent reload')
    except BaseException as e:
        sudo('sudo service iptables-persistent reload')

    sudo('service docker restart')
    sudo('iptables-save > /etc/iptables/rules.v4')


def _get_backup_to_local():
    """最新数据备份到本地"""
    with cd(_REMOTE_DIR_APP):
        tag = _datetime.now().strftime('%Y%m%d')
        tar_file_name = _TAR_FILE_TEMP.format(os.path.join(_REMOTE_DIR_APP, "www-database-backup"), tag)
        tar_files = ['volume/backup/*']
        sudo('tar -czvf {} {}'.format(tar_file_name, ' '.join(tar_files)))
        get(tar_file_name, "%s/" % _BACKUP_DIR, use_sudo=True)
            

def _make_package(file_path):
    """定义一个打包任务, 指定包名"""
    if file_path:
        if not os.path.exists('volume/restore/'):
            local('mkdir -p volume/restore/')
        if not os.path.exists(_PACKAGE_DIR):
            local('mkdir -p {}'.format(_PACKAGE_DIR))
        tar_files = ['deploy.sh', 'docker-compose-prod.yml', 'volume/restore/', 'deployment/config/']
        local('rm -f {}'.format(file_path))
        local('tar -czvf {} {}'.format(file_path, ' '.join(tar_files)))


def _upload_repo():
    """上传package,tag格式'xxxxxxxx(20180807)' """
    tag = _datetime.now().strftime('%Y%m%d')
    _TAR_FILE_NAME = _TAR_FILE_TEMP.format(_TAR_DIR_NAME, tag)
    upload_file_path = os.path.join(_PACKAGE_DIR, _TAR_FILE_NAME)
    _make_package(upload_file_path)

    # local('rsync -avz . {}:{} --delete --exclude-from \'rsync_exclude.txt\''.format(host, _REMOTE_DIR_APP))
    if not exists(_REMOTE_DIR):
        sudo('mkdir {} {}'.format(_REMOTE_DIR, _REMOTE_DIR_APP))

    put(upload_file_path, _REMOTE_DIR, use_sudo=True)

    with cd(_REMOTE_DIR):
        # 解压
        if exists(_REMOTE_DIR_APP):
            sudo('rm -rf %s' % _REMOTE_DIR_APP)
        sudo('mkdir {}'.format(_REMOTE_DIR_APP))
        sudo('tar -zxvf %s -C %s' % (_TAR_FILE_NAME, _REMOTE_DIR_APP))
        sudo('rm -f %s' % _TAR_FILE_NAME)
        # 赋权限
        sudo('chmod +x {}'.format(os.path.join(_REMOTE_DIR_APP, 'deploy.sh')))


def init_env():
    """初始化环境"""

    # try:
    #     execute(_ssh_setting, hosts=[h.replace(str(SSH_NEW_PORT), '22') for h in env.hosts])
    # except:
    #     pass

    _prepare()

    _security_setting()


def upload():
    """定义一个上传任务"""
    for host in env.hosts:
        _upload_repo()
        

def download():
    """定义一个下载任务"""
    for host in env.hosts:
        _get_backup_to_local()


def start():
    """启动 服务"""
    with cd(_REMOTE_DIR_APP):
        sudo("./deploy.sh start")


def restart():
    """重启 服务"""
    with cd(_REMOTE_DIR_APP):
        sudo("./deploy.sh restart")


def stop():
    """停止 服务"""
    with cd(_REMOTE_DIR_APP):
        sudo("./deploy.sh stop")


def pull(serverName):
    """
        拉取远程仓库的更新
        fab pull:[www-database [,www-server]]
    """
    if serverName:
        with cd(_REMOTE_DIR_APP):
            sudo("./deploy.sh pull {}".format(serverName))
