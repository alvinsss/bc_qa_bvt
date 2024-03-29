# -*- coding: utf-8 -*-
# @Time    : 2019/8/13 9:53
# @Author  : alvin
# @File    : aio_web.py
# @Software: PyCharm

import asyncio
from aiohttp import  web

async def index(request):
    '''
    asyncio实现了TCP、UDP、SSL等协议，aiohttp则是基于asyncio实现的HTTP框架。
    :param request:
    :return:
    '''
    await asyncio.sleep(0.5)
    return web.Response(body=b'<h1>Index</h1>')

async def hello(request):
    await asyncio.sleep(0.5)
    text='<h1>hello,%s!</h1>' %request.match_info['name']
    return web.Response(body=text.encode('utf-8'))

async def init(loop):
    app = web.Application(loop=loop)
    app.router.add_route('GET','/',index)
    app.router.add_route('GET','/hello/{name}',hello)

    srv = await loop.create_server(app.make_handler(),'127.0.0.1',9000)
    # aiohttp的初始化函数init()也是一个coroutine，loop.create_server()则利用asyncio创建TCP服务
    print('Server started at http://127.0.0.1:9000...')
    return srv

loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()