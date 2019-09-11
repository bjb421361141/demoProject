#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/8/18 11:02
# @Author  : Baijb
import asyncio
import functools
import inspect
import logging
import os
import re
from urllib import parse

from aiohttp import web

from www.apis import APIError

_RE_HANDLE_NAME = re.compile(r'^[0-9a-zA-Z_.]+handler$')  # handel名称匹配规则


def get(path):
    """
    定义装饰器 @get('/path')，将方法和路径的信息保存至__method__和__route__上
    :param path:
    :return:
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            return func(*args, **kw)

        wrapper.__method__ = 'GET'
        wrapper.__route__ = path
        return wrapper

    return decorator


def post(path):
    """
    定义装饰器 @post('/path')，将方法和路径的信息保存至__method__和__route__上
    :param path:
    :return:
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            return func(*args, **kw)

        wrapper.__method__ = 'POST'
        wrapper.__route__ = path
        return wrapper
    return decorator


def get_required_kw_args(fn):
    """
    获取函数中必填字段，关键字类型且默认值为空（Parameter.KEYWORD_ONLY 是跟在* 或*args参数后面的除收集关键字外的参数，调用时需要指定参数名）
    :param fn:
    :return:
    """
    args = []
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        if param.kind == inspect.Parameter.KEYWORD_ONLY and param.default == inspect.Parameter.empty:
            args.append(name)
    return tuple(args)


def get_named_kw_args(fn):
    """
    获取关键字类型的参数，包含有默认值的参数
    :param fn:
    :return:
    """
    args = []
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        if param.kind == inspect.Parameter.KEYWORD_ONLY:
            args.append(name)
    return tuple(args)


def has_named_kw_args(fn):
    """
    判断是否有关键字类型的参数，包含有默认值的参数
    :param fn:
    :return:
    """
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        if param.kind == inspect.Parameter.KEYWORD_ONLY:
            return True


def has_var_kw_arg(fn):
    """
     判断是否有收集类关键字参数
    :param fn:
    :return:
    """
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        if param.kind == inspect.Parameter.VAR_KEYWORD:
            return True


def has_request_arg(fn):
    """
    是否包含请求参数，且request后面跟的参数类型不能是
    :param fn:
    :return:
    """
    sig = inspect.signature(fn)
    params = sig.parameters
    found = False
    for name, param in params.items():
        if name == 'request':
            found = True
            continue
        if found and (param.kind != inspect.Parameter.VAR_POSITIONAL and param.kind != inspect.Parameter.KEYWORD_ONLY
                      and param.kind != inspect.Parameter.VAR_KEYWORD):
            raise ValueError(
                'request parameter must be the last named parameter in function: %s%s' % (fn.__name__, str(sig)))
    return found


class RequestHandler(object):
    """
        封装调用函数，在调用前封装请求参数
    """

    def __init__(self, app, fn):
        self._app = app
        self._func = fn
        self._has_request_arg = has_request_arg(fn)
        self._has_var_kw_arg = has_var_kw_arg(fn)
        self._has_named_kw_args = has_named_kw_args(fn)
        self._named_kw_args = get_named_kw_args(fn)
        self._required_kw_args = get_required_kw_args(fn)

    async def __call__(self, request):
        """
        RequestHandler相当于装饰器用于调用前的请求参数封装
            实现__call__方法可以使用 “实例(request)” 进行调用
        :param request:
        :return:
        """
        kw = None
        if self._has_var_kw_arg or self._has_named_kw_args or self._required_kw_args:
            if request.method == 'POST':
                if not request.content_type:
                    return web.HTTPBadRequest('Missing Content-Type.')
                ct = request.content_type.lower()
                if ct.startswith('application/json'):
                    params = await request.json()
                    if not isinstance(params, dict):
                        return web.HTTPBadRequest('JSON body must be object.')
                    kw = params
                elif ct.startswith('application/x-www-form-urlencoded') or ct.startswith('multipart/form-data'):
                    params = await request.post()
                    kw = dict(**params)
                else:
                    return web.HTTPBadRequest('Unsupported Content-Type: %s' % request.content_type)
            if request.method == 'GET':
                qs = request.query_string
                if qs:
                    kw = dict()
                    for k, v in parse.parse_qs(qs, True).items():
                        kw[k] = v[0]
        if kw is None:
            kw = dict(**request.match_info)
        else:
            if not self._has_var_kw_arg and self._named_kw_args:
                # remove all unamed kw:
                copy = dict()
                for name in self._named_kw_args:
                    if name in kw:
                        copy[name] = kw[name]
                kw = copy
            # check named arg:
            for k, v in request.match_info.items():
                if k in kw:
                    logging.warning('Duplicate arg name in named arg and kw args: %s' % k)
                kw[k] = v
        if self._has_request_arg:
            kw['request'] = request
        # check required kw:
        if self._required_kw_args:
            for name in self._required_kw_args:
                if not name in kw:
                    return web.HTTPBadRequest('Missing argument: %s' % name)
        logging.info('call with args: %s' % str(kw))
        try:
            r = await self._func(**kw)
            return r
        except APIError as e:
            return dict(error=e.error, data=e.data, message=e.message)


def add_static(app):
    """
    添加静态资源的读取路径,当前目录下的static文件夹（目前是写死静态资源的访问路径前缀和静态资源路径）
    :param app:需要注册静态资源的服务器对象
    :return:
    """
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    # url 前缀，folder路径
    app.router.add_static('/static/', path)
    logging.info('add static %s => %s' % ('/static/', path))


def add_route(app, fn):
    """
    往 app中的 UrlDispatcher(继承AbstractRouter)添加映射关系
        _resources:映射信息对象（Resource）
        _named_resources: 映射信息名称
    :param app: 需要注册映射信息的服务器对象
    :param fn: 映射方法（方法中包含 __method__ 和 __route__ 两个字段）
    :return:
    """
    method = getattr(fn, '__method__', None)
    path = getattr(fn, '__route__', None)
    if path is None or method is None:
        raise ValueError('@get or @post not defined in %s.' % str(fn))
    if not asyncio.iscoroutinefunction(fn) and not inspect.isgeneratorfunction(fn):
        fn = asyncio.coroutine(fn)
    logging.info(
        'add route %s %s => %s(%s)' % (method, path, fn.__name__, ', '.join(inspect.signature(fn).parameters.keys())))
    # 方法名，请求路径 ，处理方法
    app.router.add_route(method, path, RequestHandler(app, fn))


def add_routes(app, *module_name):
    """
    引入指定模块中的handle,取出模块中的可调用方法判断是否包含 __method__ 和 __route__属性
    :param app:
    :param module_name:
    :return:
    """
    for module in module_name:
        if not _RE_HANDLE_NAME.match(module):
            continue
        n = module.rfind('.')
        if n == (-1):
            # __import__一般用作python解释器来导入包 相当于from module import xxx
            # globals() 返回当前域内的global variables ;locals() 返回当前域内的locals variables
            mod = __import__(module, globals(), locals())
        else:
            name = module[n + 1:]
            mod = getattr(__import__(module[:n], globals(), locals(), [name]), name)
        for attr in dir(mod):
            if attr.startswith('_'):
                continue
            fn = getattr(mod, attr)
            if callable(fn):
                method = getattr(fn, '__method__', None)
                path = getattr(fn, '__route__', None)
                if method and path:
                    add_route(app, fn)
