# -*- coding: utf-8 -*-
# @Time    : 2019/7/25 18:22
# @Author  : alvin
# @File    : asyn_aiohttp.py
# @Software: PyCharm
import asyncio
import time
from aiohttp import ClientSession
from apk.AsyncHttp import AsyncHTTP
#async英文为异步的+io操作
url = 'https://api.github.com/events'
#url = 'http://10.21.21.248:8002/sr_sys/v1/user/list'
now = lambda: time.time()
if __name__ == '__main__':
    start = now()
    #方法可以创建一个事件循环,asyncio.BaseEventLoop。
    #协程对象不能直接运行，在注册事件循环的时候，其实是run_until_complete方法将协程包装成为了一个任务（task）对象。
    #所谓task对象是Future类的子类。保存了协程运行后的状态，用于未来获取协程的结果
    loop = asyncio.get_event_loop()
    #方法可以创建一个事件循环,asyncio.BaseEventLoop。
    #协程对象不能直接运行，在注册事件循环的时候，其实是run_until_complete方法将协程包装成为了一个任务（task）对象。
    #所谓task对象是Future类的子类。保存了协程运行后的状态，用于未来获取协程的结果
    # loop = asyncio.get_event_loop()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop( loop )
    # 因为asyncio程序中的每个线程都有自己的事件循环，但它只会在主线程中为你自动创建一个事件循环。所以如果你asyncio.get_event_loop
    # 在主线程中调用一次，它将自动创建一个循环对象并将其设置为默认值，但是如果你在一个子线程中再次调用它，你会得到这个错误。相反，您
    # 需要在线程启动时显式创建 / 设置事件循环： loop = asyncio.new_event_loop()  asyncio.set_event_loop(loop)

    #     #需要处理的任务
    #tasks = [loop.create_task(AsyncHTTP.get(url)) for i in range(512)] 确定参数是协程的时候可以用这个
    #需要处理的任务
    # tasks = [asyncio.ensure_future(AsyncHTTP.get(url))]
    # tasks = [asyncio.ensure_future( AsyncHTTP.post('http://httpbin.org/post', data = {'key':'value'})) ]

    list1 = [1,2,3]
    for i in list1:
        if i == 1:
            tasks = [asyncio.ensure_future( AsyncHTTP.post( 'http://httpbin.org/post', data={'key': 'value'} ) )]
        if i == 2:
            tasks = [asyncio.ensure_future( AsyncHTTP.get( 'https://api.github.com/events') )]

    # tasks = [asyncio.ensure_future(req_post(url))]

    #tasks = [loop.create_task(req_get(url)) for i in range(512)] 确定参数是协程的时候可以用这个
    #将协程注册到事件循环，并启动事件循环
    #loop.run_until_complete(asyncio.gather(*tasks))
    loop.run_until_complete(asyncio.wait(tasks))
    count = 0
    for task in tasks:
        print(task)
        print('Task ret: ', task.result())
        if len(task.result()):
            count=count+1
    print('TIME: ', now() - start,count)