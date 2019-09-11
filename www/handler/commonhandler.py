#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/8/20 19:42
# @Author  : Baijb
import asyncio
import hashlib
import logging
import time

from www.apis import APIPermissionError
from www.config import configs
from www.coreweb import get
from www.model import User, Blog, Page

"""
    业务处理
    ****   REST（Representational State Transfer） 软件架构模式
        httpclient + url 取代 传统的SOAP（例如 Web Services）服务调用模式
"""


def check_admin(request):
    if request.__user__ is None or not request.__user__.admin:
        raise APIPermissionError()


@get('/')
async def index(request):
    users = await User.findAll()
    return {
        '__template__': 'example.html',
        'users': users
    }


@get('/api/users')
async def api_get_users(*, page='1'):
    """
    返回json格式的数据
    :param page:
    :return:
    """
    # page_index = get_page_index(page)
    num = await User.findNumber('count(id)')
    p = Page(10, int(num))
    pageinf = p.get_page_info(int(page))
    if num == 0:
        return dict(page=pageinf, users=())
    users = await User.findAll(orderBy='created_at desc', limit=(pageinf.offset, pageinf.page_size))
    for u in users:
        u.passwd = '******'
    return dict(page=pageinf, users=users)


@get('/register')
def register():
    return {
        '__template__': 'register.html'
    }
