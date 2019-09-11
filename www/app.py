#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/8/9 11:00
# @Author  : Baijb

"""
    demoProject 的web服务器(异步io处理高并发访问，使用单线程及协程处理)
        ---路径映射（web.Application 中 ） 和 视图处理器（jinja2）
    1、生成数据连接池
    2、生成web服务器对象（设置 middlewares（类似拦截器） 日志处理，返回值处理）
    3、生成jinja2（viewResolver）
    4、添加业务处理层（路径-方法映射）
    5、添加静态资源访问路径
    6、运行web 服务器对象

    运行流程：
        1、客户端发送请求
        2、web端接收请求，找到web中对应的映射的handle
        3、循环middlewares
        4、
"""
import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime

from aiohttp import web
from jinja2 import Environment, FileSystemLoader

from www import orm
from www.config import configs
from www.coreweb import add_routes, add_static

logging.basicConfig(level=logging.INFO)


def init_jinja2(app, **kw):
    """
    设置viewResolver
    :param app:
    :param kw:
    :return:
    """
    logging.info('init jinja2...')
    options = dict(
        autoescape=kw.get('autoescape', True),
        block_start_string=kw.get('block_start_string', '{%'),
        block_end_string=kw.get('block_end_string', '%}'),
        variable_start_string=kw.get('variable_start_string', '{{'),
        variable_end_string=kw.get('variable_end_string', '}}'),
        auto_reload=kw.get('auto_reload', True)
    )
    path = kw.get('path', None)
    if path is None:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    logging.info('set jinja2 template path: %s' % path)
    env = Environment(loader=FileSystemLoader(path), **options)
    filters = kw.get('filters', None)
    if filters is not None:
        for name, f in filters.items():
            env.filters[name] = f
    app['__templating__'] = env


async def data_factory(app, handler):
    """
    处理请求参数，处理成dict对象并放入request的__data__属性中
    response = await handler(request) 调用下一个处理器
    :param app:
    :param handler:
    :return:
    """

    async def parse_data(request):
        if request.method == 'POST':
            if request.content_type.startswith('application/json'):
                request.__data__ = await request.json()
                logging.info('request json: %s' % str(request.__data__))
            elif request.content_type.startswith('application/x-www-form-urlencoded'):
                request.__data__ = await request.post()
                logging.info('request form: %s' % str(request.__data__))
        return (await handler(request))

    return parse_data


async def logger_factory(app, handler):
    async def logger(request):
        logging.info('Request: %s %s' % (request.method, request.path))
        return (await handler(request))

    return logger


async def response_factory(app, handler):
    async def response(request):
        logging.info('Response handler...')
        r = await handler(request)
        if isinstance(r, web.StreamResponse):
            return r
        if isinstance(r, bytes):
            resp = web.Response(body=r)
            resp.content_type = 'application/octet-stream'
            return resp
        if isinstance(r, str):
            if r.startswith('redirect:'):
                return web.HTTPFound(r[9:])
            resp = web.Response(body=r.encode('utf-8'))
            resp.content_type = 'text/html;charset=utf-8'
            return resp
        if isinstance(r, dict):
            template = r.get('__template__')
            if template is None:
                resp = web.Response(
                    body=json.dumps(r, ensure_ascii=False, default=lambda o: o.__dict__).encode('utf-8'))
                resp.content_type = 'application/json;charset=utf-8'
                return resp
            else:
                resp = web.Response(body=app['__templating__'].get_template(template).render(**r).encode('utf-8'))
                resp.content_type = 'text/html;charset=utf-8'
                return resp
        if isinstance(r, int) and 100 <= r < 600:
            return web.Response(r)
        if isinstance(r, tuple) and len(r) == 2:
            t, m = r
            if isinstance(t, int) and 100 <= t < 600:
                return web.Response(t, str(m))
        # default:
        resp = web.Response(body=str(r).encode('utf-8'))
        resp.content_type = 'text/plain;charset=utf-8'
        return resp

    return response


def datetime_filter(t):
    """
     jinja2自定义filter，模板文件中可以直接使用方法来输出内容
    :param t:
    :return:
    """
    delta = int(time.time() - t)
    if delta < 60:
        return u'1分钟前'
    if delta < 3600:
        return u'%s分钟前' % (delta // 60)
    if delta < 86400:
        return u'%s小时前' % (delta // 3600)
    if delta < 604800:
        return u'%s天前' % (delta // 86400)
    dt = datetime.fromtimestamp(t)
    return u'%s年%s月%s日' % (dt.year, dt.month, dt.day)


async def init(loop):
    await orm.create_pool(loop=loop, host=configs.db.host, port=configs.db.port, user=configs.db.user,
                          password=configs.db.password, db=configs.db.db)
    app = web.Application(loop=loop, middlewares=[
        logger_factory, data_factory, response_factory
    ])
    init_jinja2(app, filters=dict(datetime=datetime_filter))
    add_routes(app, *configs.web.handlers)
    add_static(app)
    runner = web.AppRunner(app)
    await runner.setup()
    port = 9000 if not configs.web.port else configs.web.port
    site = web.TCPSite(runner, '127.0.0.1', port)
    logging.info('server started at http://127.0.0.1:%s...' % port)
    await site.start()


# curPath = os.path.abspath(os.path.dirname(__file__))
# sys.path.append(os.path.split(curPath)[0])

# 添加模块


loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()
