# -*- coding: utf-8 -*-
# @Time    : 2019/7/25 12:09
# @Author  : alvin
# @File    : AsyncHttp.py
# @Software: PyCharm
from apk.AsyncHttp import AsyncHTTP
import asyncio

def qatest():
    url ='https://api.github.com/events'
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(AsyncHTTP.get(url))
    result_post = loop.run_until_complete(AsyncHTTP.post("http://httpbin.org/post", data = {'key':'value'}))
    loop.close()

tasks = []
url = "https://www.baidu.com/{}"

if  __name__ == '__main__':
    qatest()
    # loop = asyncio.get_event_loop()
