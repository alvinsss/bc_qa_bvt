# -*- coding: utf-8 -*-
# @Time    : 2019/7/25 15:22
# @Author  : alvin
# @File    : thread_all.py
# @Software: PyCharm

import asyncio
import time
now = lambda: time.time()
from threading import Thread
from apk.AsyncHttp import  AsyncHTTP
#     '''
#     新线程协程的话，可以在主线程中创建一个new_loop，然后在另外的子线程中开启一个无限事件循环。主线程通过run_coroutine_threadsafe新注册协程对象。这样就能在子线程中进行事件循环的并发操作，
# 同时主线程又不会被block。一共执行的时间大概在6s左右。
#     :param loop:
#     :return:
#     '''

def start_loop(loop):
    asyncio.set_event_loop( loop )
    loop.run_forever()


async def do_some_work(x):
    print( 'Waiting {}'.format( x ) )
    await asyncio.sleep( x )
    print( 'Done after {}s'.format( x ) )


def more_work(x):
    print( 'More work {}'.format( x ) )
    time.sleep( x )
    AsyncHTTP.get("https://api.github.com/events")
    print( 'Finished more work {}'.format( x ) )

start = now()
new_loop = asyncio.new_event_loop()
t = Thread( target=start_loop, args=(new_loop,) )
t.start()
print( 'TIME: {}'.format( time.time() - start ) )

asyncio.run_coroutine_threadsafe( more_work(6), new_loop )
asyncio.run_coroutine_threadsafe( more_work(3), new_loop )
