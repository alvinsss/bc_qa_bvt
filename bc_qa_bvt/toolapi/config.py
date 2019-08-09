#coding:utf-8
import os
import re

class basedata:
    TESTMODE = False
    curdir = os.getcwd()
    
    if TESTMODE:
        MYSQL_HOST='127.0.0.1'
        MYSQL_USER='root'
        MYSQL_PWD='123456'
        MYSQL_DB='apkinfo'
        MYSQL_PORT=3306
        
        aaptpath = os.path.abspath(os.path.dirname(__file__)) + "/tools/forapk/"
        apkInfoQueryUrl = 'http://localhost:9019/apkinfo/query?taskid='
        updateTaskResutlFormat = 'json'
    else:
        MYSQL_HOST='172.31.1.12'
        MYSQL_USER='dev'
        MYSQL_PWD='qatest'
        MYSQL_DB='apitestserver'
        MYSQL_PORT=3306
        
        aaptpath = "/opt/android-sdk/build-tools/build-tools/27.0.3/"
        apkInfoQueryUrl = 'http://172.31.1.12:9019/apkinfo/query?taskid='
        updateTaskResutlFormat = 'html'