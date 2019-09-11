#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/9/6 10:38
# @Author  : Baijb 

"""
Fabric 发布工具
需要根据开发环境的系统情况修改命令
"""

import os, re

from datetime import datetime
from fabric.api import *

# linux 服务器信息
env.user = 'root'  # 用于部署的用户
env.sudo_user = 'root'
env.hosts = ['192.168.245.128']

# mysql 数据库信息
db_user = 'crawl'
db_password = 'password'

# 设置常量信息
_PRJECT_NAME = 'demoProject'  # 设置项目名称
_TAR_FILE = 'dist-%s.tar.gz' % _PRJECT_NAME
_REMOTE_TMP_TAR = '/tmp/%s' % _TAR_FILE
_REMOTE_BASE_DIR = '/home/baijb/srv/demoProject'


def _current_path():
    return os.path.abspath('.')


def _now():
    return datetime.now().strftime('%y-%m-%d_%H.%M.%S')


def build():
    """
    编译并打包发布版本
    """
    includes = ['handler', 'static', 'templates', '*.py']
    excludes = ['test', '.*', '*.pyc', '*.pyo', 'config_override.py']
    if os.path.isfile("dist/%s" % _TAR_FILE):
        local(r'del dist\%s' % _TAR_FILE)  # del 删除文件 rd 删除目录
    with lcd(os.path.join(_current_path(), 'www')):
        cmd = ['tar', '-czvf', r'..\dist\%s' % _TAR_FILE]
        cmd.extend(['--exclude=%s' % ex for ex in excludes])
        cmd.extend(includes)
        local(' '.join(cmd))


def deploy():
    newdir = 'www-%s' % _now()
    run('rm -f %s' % _REMOTE_TMP_TAR)
    put('dist/%s' % _TAR_FILE, _REMOTE_TMP_TAR)
    with cd(_REMOTE_BASE_DIR):
        sudo('mkdir %s' % newdir)
    with cd('%s/%s' % (_REMOTE_BASE_DIR, newdir)):
        sudo('tar -xzvf %s' % _REMOTE_TMP_TAR)
    with cd(_REMOTE_BASE_DIR):
        sudo('rm -f www')
        sudo('ln -s %s www' % newdir)
        # 非所有人的执行权限 才需要执行以下语句
        # sudo('chown www-data:www-data www')
        # sudo('chown -R www-data:www-data %s' % newdir)
    with settings(warn_only=True):
        sudo('supervisorctl stop %s' % _PRJECT_NAME)
        sudo('supervisorctl start  %s' % _PRJECT_NAME)
        sudo('nginx reload')


def chmod():
    # 递归目录将所属组的权限修改成属组权限
    pass


def start_mysql():
    sudo('systemctl start mysql')


def start_nginx():
    sudo('nginx -c /usr/local/nginx/conf/nginx.conf')


if __name__ == "__main__":
    build()
    deploy()
