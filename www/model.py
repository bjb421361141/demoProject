#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/8/16 16:33
# @Author  : Baijb

import time, uuid

import math

from www.orm import Model, StringField, BooleanField, FloatField, TextField


# 生成50位唯一编码
def next_id():
    return '%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex)


class User(Model):
    __table__ = 'users'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    email = StringField(ddl='varchar(50)')
    passwd = StringField(ddl='varchar(50)')
    admin = BooleanField()
    name = StringField(ddl='varchar(50)')
    image = StringField(ddl='varchar(500)')
    created_at = FloatField(default=time.time)


class Blog(Model):
    __table__ = 'blogs'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    user_id = StringField(ddl='varchar(50)')
    user_name = StringField(ddl='varchar(50)')
    user_image = StringField(ddl='varchar(500)')
    name = StringField(ddl='varchar(50)')
    summary = StringField(ddl='varchar(200)')
    content = TextField()
    created_at = FloatField(default=time.time)


class Comment(Model):
    __table__ = 'comments'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    blog_id = StringField(ddl='varchar(50)')
    user_id = StringField(ddl='varchar(50)')
    user_name = StringField(ddl='varchar(50)')
    user_image = StringField(ddl='varchar(500)')
    content = TextField()
    created_at = FloatField(default=time.time)


class Page(dict):
    """
        定义分页信息

    """
    __porperties = ("page_size", "total_num")

    def __init__(self, page_size, total_num):
        kw = {'page_size': page_size if page_size and isinstance(page_size, int) else 10,
              'total_num': 0 if not isinstance(total_num, int) else total_num,
              'page_num': 0,
              'offset': 0
              }
        super(Page, self).__init__(**kw)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'没有该属性值 '%s'" % key)

    def __setattr__(self, key, value):
        if key in self.__porperties:
            if not isinstance(value, int):
                raise ValueError(r"'该属性值应该为int类型 '%s'" % key)
            self[key] = value
        else:
            raise AttributeError(r"只允许设置以下属性 '%s'" % ",".join(self.__porperties))

    def get_page_info(self, pagenum):
        if not isinstance(pagenum, int):
            raise AttributeError(r"''该属性值应该为int类型 'pagenum'")
        max_page_size = self.total_num / self.page_size
        pagenum = pagenum if pagenum <= math.ceil(max_page_size) else max_page_size
        self["page_num"] = pagenum
        self["offset"] = 0 if pagenum <= 0 else (pagenum - 1) * 5+1
        return self


if __name__ == "__main__":
    p = Page(10,21)
    print(type(p.get_page_info(3)),p.get_page_info(3).offset)