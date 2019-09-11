#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/8/13 16:49
# @Author  : Baijb
import asyncio
import time
import uuid
from random import randint

from www import orm, model
from www.orm import Model, StringField, BooleanField, FloatField

DB_HOST = '192.168.245.128'
DB_USER = 'crawl'
DB_PASSWORD = 'password'
DB_PORT = 3306
DB_NAME = 'CRAWL_DB'
DB_CHARSET = 'utf8'


def next_id():
    return '%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex)


@asyncio.coroutine
def test():
    yield from orm.create_pool(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, port=DB_PORT, db=DB_NAME)
    for x in range(10):
        u = model.User(name='Test%s' % x, email='test%s@example.com' % x, passwd='1234567890', image='about:blank')
        yield from u.save()


class Human(object):
    def __init__(self, name, gender):
        print("这边有调用Human的__init__方法")
        self.name = name
        self.gender = gender

    def __new__(cls, *args, **kwargs):
        print("这边有调用Human的__new__方法,cls:%s" + str(cls))
        for x in args:
            print(x)
        for x,y in kwargs:
            print(x,y)
        return object.__new__(cls)

    def s(self):
        print("方法s")


class StudentMate(type):
    def __init__(self, name, gender):
        print("这边有调用Student的__init__方法")
        self.name = name
        self.gender = gender

    def __new__(cls, *args, **kwargs):
        print("这边有调用Student的__new__方法,cls:%s" + cls)
        return object.__new__(cls)


class Student(Human):
    pass


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test())
    # u = Student("a", 'sex')
    # print(dir(u))
    # h = Human("a", 'sex')
    # print(type(u))
