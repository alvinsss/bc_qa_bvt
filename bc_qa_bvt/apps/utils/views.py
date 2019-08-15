"""
@author:alvin
@time: 2019/08/13
"""
# !usr/bin/env python
# -*- coding:utf-8

# Create your views here.

from apps.utils.log import default_log
from apps.utils.exception.my_exception import MyException
from apps.utils.http_format import response_success,response_failed

def test_success(request):
    a = 2
    b = 2
    c = 2
    if a != 1:
        raise MyException(message="a is wrong")

    if b != 1:
        raise MyException(message="b is wrong")
    if c !=1:
        raise MyException(message="c is wrong")
    return response_success({"a": 1})


def test_failed(request):
    default_log.error("error-1")
    return response_failed(10000, "普通错误")
