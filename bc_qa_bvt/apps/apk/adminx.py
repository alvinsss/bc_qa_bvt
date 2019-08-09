#!usr/bin/env python
# -*- coding:utf-8
"""
@author:alvin
@file: xadmin.py
@time: 2019/05/12
"""
import xadmin
from .models import APK_UPLOADFILE,APK_RESULTS

class APK_UPLOADFILEAdmin(object):
	list_display = [ 'name_des', 'upfilepath', 'sum_status','sum_result','create_time']
	list_display = [ 'name_des', 'upfilepath', 'sum_status','sum_result']
	list_display = [ 'name_des', 'upfilepath', 'sum_status','sum_result','create_time']

xadmin.site.register(APK_UPLOADFILE, APK_UPLOADFILEAdmin)

class APK_RESULTSAdmin(object):
	list_display = [ 'name_des', 'upfilepath','apkfile_path','apk_testtype', 'run_status','run_result','create_time']
	list_display = [ 'name_des', 'upfilepath','apkfile_path','apk_testtype', 'run_status','run_result']
	list_display = [ 'name_des', 'upfilepath','apkfile_path','apk_testtype', 'run_status','run_result','create_time']

xadmin.site.register(APK_RESULTS, APK_RESULTSAdmin)