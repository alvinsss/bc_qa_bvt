# -*- coding: utf-8 -*-
# @Time    : 2019/7/31 16:23
# @Author  : alvin
# @File    : test_downloadfile.py
# @Software: PyCharm

import  requests
import os


class Testapkfile(object):

    def __init__(self):
        self.r = requests.get(url="http://172.31.1.12:8008/apk/download_apkfile/66")

    def test_write_file(self,dir,filename):
        r = self.r
        print("test_write_file")
        print(r)
        path = os.path.join(dir,filename)
        print(path)
        if r.status_code == 200:
            with open(path,'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    f.write(chunk)
            print("write is ok!")

if __name__ == "__main__":
    f = Testapkfile()
    filename = "6.apk"
    dir='D:\static\qatest'
    f.test_write_file(dir,filename)