#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/8/20 19:01
# @Author  : Baijb

configs = {
    'debug': False,
    'db': {
        'host': '127.0.0.1',
        'port': 3306,
        'user': 'crawl',
        'password': 'password',
        'db': 'CRAWL_DB'
    },
    'web': {
        'server': '127.0.0.1',
        'port': 9000,
        'handlers': {
            "www.handler.blogshandler",
            "www.handler.commonhandler",
            "www.handler.loginhandler"
        }
    },
    'session': {
        'secret': 'Awesome'
    }

}
