#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/8/31 15:44
# @Author  : Baijb
import time

from www.apis import APIValueError
from www.coreweb import get, post
from www.handler import commonhandler
from www.model import Blog


"""
    传统的MVC 中使用的VIEW 一般为通过后端生成的。一定程度影响了复用（后端技术框架改变后无法再使用前端的页面） 
    新的MVVM：Model View ViewModel模式应运而生。MVVM最早由微软提出来，它借鉴了桌面应用程序的MVC思想，在前端页面中，把Model用纯JavaScript对象表示：
    Model和View 的操作通过javascript来进行操作，view直接是单纯的HTML
    
    前端处理：
        jquery:一般用于渲染和动画处理
        vue：（MVVM框架）一般用于处理数据和页面的绑定
"""


@get('/blogs')
async def blogs(request):
    # 获取 Page信息和分页 blogs数据信息
    return {
        '__template__': 'blogs.html',
    }


@get('/manage_blogs')
async def manage_blogs(request):
    # 获取博客页面信息
    return {
        '__template__': 'manage_blog_edit.html'
    }


@post('/api/blogs')
def api_create_blog(request, *, name, summary, content):
    commonhandler.check_admin(request)
    # 字段校验
    if not name or not name.strip():
        raise APIValueError('name', 'name cannot be empty.')
    if not summary or not summary.strip():
        raise APIValueError('summary', 'summary cannot be empty.')
    if not content or not content.strip():
        raise APIValueError('content', 'content cannot be empty.')
    blog = Blog(user_id=request.__user__.id, user_name=request.__user__.name, user_image=request.__user__.image,
                name=name.strip(), summary=summary.strip(), content=content.strip())
    yield from blog.save()
    return blog
