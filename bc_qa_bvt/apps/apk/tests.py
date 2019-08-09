from django.test import TestCase
from apk.models import APK_RESULTS
from module.models import Module
from apk.models import APK_UPLOADFILE
from django.test import Client
import  requests
from django.conf import settings
from functools import wraps
import json

class ApkUploadFileTest(TestCase):

    def setUp(self):
        Module.objects.create( id=1,name="qatest", describe="qatest11", project="qqqq" )
        APK_UPLOADFILE.objects.create( module_id=1, userid="9999", username="qatest", name_des="unittest",
                                       upfilepath="/export/server/pref/apk/uploads/admin/2019-07-11_12:47:22/app-app_gnbs_east-release_new.apk", apk_testtype="['Apkinfo,Monkey,Seccheck,VirusScanning']" )


    # 测试上传文件
    def test_query_uploadfile(self):
        info = APK_UPLOADFILE.objects.get(username="qatest")
        names_des = info.name_des
        apk_testtype = info.apk_testtype
        self.assertEquals(names_des,"unittest")
        self.assertEquals(apk_testtype,"['Apkinfo,Monkey,Seccheck,VirusScanning']")

    def test_run_task(self):
        data = {
            "taskid": 38,
            "path": '/export/server/pref/apk/uploads/AnonymousUser/2019-07-26_11:20:08/HwMultiScreenShot.apk'  #当不支持zip的格式直接读此数据即可
        }
        r_monkey = requests.post( settings.MONKEY_URL, data )
        print( "r_monkey text:", r_monkey.text )
        print( "r_monkey status:", r_monkey.status_code )

    def test_run_task(self):
        pass

    def test_str(self):
        a=['手势服务']
        print(a[2:-3])



if __name__ == "__main__":
    headers = {'User-Agent': 'Mozilla、5.0'}()