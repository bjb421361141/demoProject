#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/8/13 14:33
# @Author  : Baijb
import asyncio
import unittest

from www import orm
from www.orm import Model, StringField

DB_HOST = '192.168.245.128'
DB_USER = 'crawl'
DB_PASSWORD = 'password'
DB_PORT = '3306'
DB_NAME = 'CRAWL_DB'
DB_CHARSET = 'utf8'


class TestOrm(unittest.TestCase):
    """
        继承Model类
    """

    class User(Model):
        # 定义类的属性到列的映射：
        id = StringField('id', primary_key=True)
        name = StringField('username')
        email = StringField('email')
        password = StringField('password')

    def setUp(self):
        print('运行整个单元测试的开端 setUp')

    def tearDown(self):
        print('运行整个单元测试的结束 tearDown...')

    async def test_saveModel(self):
        print("===============测试数据加载===================")
        await orm.create_pool(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, port=DB_PORT, db=DB_NAME)
        u = TestOrm.User(id=12345, name='Michael22', email='test@orm.org', password='my-pwd')
        await u.save()
        print(dir(u))
        print(u["name"])
        u = TestOrm.User.load(pk=12345)
        print(u)


if __name__ == '__main__':
    # unittest.main()
    # TestStudent.test_saveModel()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(TestOrm.test_saveModel())
