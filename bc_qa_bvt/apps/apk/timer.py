# -*- coding: utf-8 -*-
# @Time    : 2019/7/30 12:05
# @Author  : alvin
# @File    : timer.py
# @Software: PyCharm
from functools import wraps
import time

def print_func_time(function):
    '''
    计算程序运行时间,time.time()是统计的wall time(即墙上时钟)
    time.clock()是统计cpu时间 的工具，这在统计某一程序或函数的执行速度最为合适。两次调用time.clock()函数的插值即为程序运行的cpu时间。
    :param function:
    :return:
    '''
    @wraps( function )
    def func_time(*args, **kwargs):
        t0 = time.clock()
        t0_time = time.time()
        result = function( *args, **kwargs )
        t1 = time.clock()
        t1_time = time.time()
        print( "Total running clock() time: %s s" % (str( t1 - t0 )) )
        print( "Total running time() time: %s s" % (str( t1_time - t0_time )) )
        return result
    return func_time

@print_func_time
def test():
    print( "qa" )