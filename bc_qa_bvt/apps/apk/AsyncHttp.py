# -*- coding: utf-8 -*-
# @Time    : 2019/7/25 12:09
# @Author  : alvin
# @File    : AsyncHttp.py
# @Software: PyCharm
import  aiohttp
import  json
class AsyncHTTP(object):
    '''
    aiohttp封装，实现了get/post方法
    :return:
    '''
    async def post(url, data, headers=None):
        async with aiohttp.ClientSession( headers=headers ) as session:
            result = await session.post( url, data=data )
            print("post result get json result ---->",result)
            return await result.json()

    async def post_json(url, data):
        headers = {'Content-Type': 'application/json'}
        async with aiohttp.ClientSession( headers=headers ) as session:
            result = await session.post( url, json=data )
            print("post_json",data)
            print("post_json result get json result ---->",result)
            return await result.text()


    async def post_text_plain(url, data, headers=None):
        async with aiohttp.ClientSession( headers=headers ) as session:
            result = await session.post( url, data=data )
            print("post_text_plain result text---->",result)
            return await result.text()

    async def get(url, headers=None, **kwargs):
        async with aiohttp.ClientSession( headers=headers ) as session:
            result = await session.get( url, data=kwargs)
            print("get result---->",result)
            return await result.json()

    async def put(url, data, headers=None):
        async with aiohttp.ClientSession( headers=headers ) as session:
            result = await session.put( url, data=data )
            return await result.json()
