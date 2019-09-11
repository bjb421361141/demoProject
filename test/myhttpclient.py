#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/8/23 15:09
# @Author  : Baijb
import requests
from urllib import request as urllib_request

# 使用request包请求数据
url = "http://127.0.0.1:9000/blog"
headers = {'Content-Type': ''}
rep = requests.get(url, headers=headers)
print(rep.content)

# 使用urllib 请求数据
# req = urllib_request.Request(url)
# req.add_header('Content-Type', '')
# with urllib_request.urlopen(req, data="{}".encode('utf-8')) as f:
#     print('Status:', f.status, f.reason)
#     for k, v in f.getheaders():
#         print('%s: %s' % (k, v))
#     print('Data:', f.read().decode('utf-8'))
