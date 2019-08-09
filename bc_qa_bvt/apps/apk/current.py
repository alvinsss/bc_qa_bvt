# -*- coding: utf-8 -*-
# @Time    : 2019/7/25 17:09
# @Author  : alvin
# @File    : current.py
# @Software: PyCharm
import asyncio
import threading
import time
now = lambda: time.time()

@asyncio.coroutine
def hello():
    '''
    并发执行
    :return:
    '''
    print('Hello world! (%s)' % threading.currentThread())
    yield from asyncio.sleep(1)
    print('Hello again! (%s)' % threading.currentThread())

# 获取EventLoop:
start = now()
loop = asyncio.get_event_loop()
tasks = [hello(), hello()]
loop.run_until_complete(asyncio.wait(tasks))
loop.close()
print( 'TIME: {}'.format( time.time() - start ) )

