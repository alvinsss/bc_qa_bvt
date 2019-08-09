#coding:utf-8
import re
import time
import base64
import hashlib
import os
import json
import zipfile
from urllib import parse
import toolDB
import global_var
import config

datains = config.basedata()
aaptpath = datains.aaptpath
updateTaskResutlFormat = datains.updateTaskResutlFormat
 
class Tools:
    def base64py(self, instr, type="encode"):
        try:
            if type == "decode":
                ret = base64.b64decode(instr)
                return ret.decode()
            else:
                ret = base64.b64encode(instr)
                return ret.decode()
        except Exception:
            return None
        
    def md5str(self, data):
        try:
            m = hashlib.md5()
            m.update(data)
            return m.hexdigest()
        except Exception:
                return None
    
    def md5File(self, path, size = 32768):
        try:
            if not os.path.exists(path):
                return ''
            m = hashlib.md5()
            f = open(path, 'rb')
            while True:
                d = f.read(size)
                if not d:
                    break
                m.update(d)
            f.close()
            return m.hexdigest()
        except Exception:
            return None
 
    def getPathDirName(self,path):
        return os.path.dirname(path)
   
    def getApkSigns(self, apkfile):
        apk_md5 = ''
        apk_sha1 = ''
        apk_sha256 = ''
        nowtime = int(time.time())
        zFile = zipfile.ZipFile(apkfile, "r")
        basedir = self.getPathDirName(apkfile)
        zipdir = basedir + '/' + str(nowtime) + '/'
        
        for fileM in zFile.namelist(): 
            zFile.extract(fileM, zipdir)
        zFile.close();
        
        cmdline = 'keytool -printcert -file %sMETA-INF/*.RSA' % zipdir
        md5regex = r'.*(MD5:)\s+([\w\d\.\:]+)'
        sha1regex = r'.*(SHA1:)\s+([\w\d\.\:]+)'
        sha256regex = r'.*(SHA256:)\s+([\w\d\.\:]+)'
        getInfoList = None
        try:
            getInfoList = os.popen(cmdline).readlines()
        except:
            pass
        if getInfoList and isinstance(getInfoList, list):
            if 'keytool' in getInfoList[0]:
                return None
            else:
                for i in range(len(getInfoList)):
                    comReg_md5 = re.compile(md5regex)
                    m = comReg_md5.search(getInfoList[i])
                    if m:
                        apk_md5 = m.group(2)
                    comReg_sha1 = re.compile(sha1regex)
                    s1 = comReg_sha1.search(getInfoList[i])
                    if s1:
                        apk_sha1 = s1.group(2)
                    comReg_sha256 = re.compile(sha256regex)
                    s256 = comReg_sha256.search(getInfoList[i])
                    if s256:
                        apk_sha256 = s256.group(2)
                ret = (apk_md5, apk_sha1, apk_sha256)
                return ret
        else:
            return None
    
    def getApkInfo_byUpload(self, uploadpath):
        info = {}
        path = aaptpath
        aapt_path = path + "aapt" 
        get_info_command = "%s dump badging %s" % (aapt_path, uploadpath)
        output = os.popen(get_info_command).read()
        match = re.compile("package: name='(\S+)' versionCode='(\d+)' versionName='(\S+)'").match(output)
        if not match:
            return None
        info["packagename"] = match.group(1)
        info["versionCode"] = match.group(2)
        info["versionName"] = match.group(3)
        
        apkfile = os.path.abspath(uploadpath)
        apksigninfo = self.getApkSigns(apkfile)
        if apksigninfo:
            info["MD5"] = apksigninfo[0]
            info["SHA1"] = apksigninfo[1]
            info["SHA256"] = apksigninfo[2]
        
        filemd5 = self.md5File(apkfile, size = 32768)
        if filemd5:
            info["apk_md5"] = filemd5
        filesize = os.path.getsize(apkfile)
        if filesize:
            info["apk_size"] = filesize 
        return info
            
    def getapkinfo_intoDB(self,uploadpath,taskid,downloadUrl=None,needUpdateApkInfo=False): # 解析apk文件，存入数据库，并更改任务状态
        info = self.getApkInfo_byUpload(uploadpath)
        run_status = 0 # 0未执行，1 执行中，2 执行完成，3 排队中
        run_result = 0 # 0 未知，1 成功，2 失败
        detail = ''
        if not info:
            run_status = 2
            run_result = 2
            updateResultSql = "update apk_apk_results set run_status=%d,run_result=%d' where task_id=%d and apk_testtype='Apkinfo';" % (run_status,run_result,int(taskid))
            ins_db = toolDB.Sql()
            ins_db.update(updateResultSql)
            ins_db.closedb()
            return None
        file_md5 = info["apk_md5"]
        file_size = info["apk_size"]
        package_name = info["packagename"]
        version_name = info["versionName"]
        file_path = ''
        if downloadUrl:
            file_path = downloadUrl
        else:
            file_path = uploadpath
        result_json = json.dumps(info)
        result_html = ''
        if result_json:
            result_html = self.jsonStr2HtmlStr(result_json)
        querySql = "select file_md5 from apk_apk_info where file_md5='%s';" % file_md5
        ins_db = toolDB.Sql()
        qret = ins_db.query(querySql)
        ins_db.closedb()
        
        qret_res = None
        if not qret:
            pass
        else:
            qret_res = qret[0][0]
        
        updateApkInfoFlag = False
        if not qret_res or qret_res=='':
            updateApkSql = "insert into apk_apk_info(file_md5,file_size,package_name,version_name,file_path,result_json,result_html) "\
                        "values ('%s',%d,'%s','%s','%s','%s','%s');" % (file_md5,file_size,package_name,version_name,file_path,result_json,result_html)
            ins_db = toolDB.Sql()
            updateApkInfoFlag = ins_db.update(updateApkSql)
            ins_db.closedb()
        else:
            if needUpdateApkInfo:
                updateApkSql = "update apk_apk_info set file_size=%d,package_name='%s',version_name='%s',file_path='%s',result_json='%s',result_html='%s' "\
                            "where file_md5='%s';" % (file_size,package_name,version_name,file_path,result_json,result_html,file_md5)
                ins_db = toolDB.Sql()
                updateApkInfoFlag = ins_db.update(updateApkSql)
                ins_db.closedb()
                
        if file_md5 and updateApkInfoFlag:
            updateTaskSql = "update apk_task_info set status=1,file_md5='%s' where task_id=%d;" % (file_md5, int(taskid))
            ins_db = toolDB.Sql()
            updateTaskFlag = ins_db.update(updateTaskSql)
            ins_db.closedb()
        if updateTaskFlag:
            if updateTaskResutlFormat == 'html':
                detail = result_html
            else:
                detail = result_json
            if detail == '' or not detail:
                run_status = 2
                run_result = 2
            else: 
                run_status = 2
                run_result = 1
            
            updateResultSql = "update apk_apk_results set run_status=%d,run_result=%d,detail='%s' where task_id=%d and apk_testtype='Apkinfo';" % (run_status,run_result,detail,int(taskid))
            ins_db = toolDB.Sql()
            ins_db.update(updateResultSql)
            ins_db.closedb()

    def queue_consumer(self,eachTaskSleep,overWriteApkInfo=False):
        while True:
            try:
                taskqueue = global_var.get_value('queue') #尝试获取
                if taskqueue.is_empty():
                    pass
                else:
                    taskqueue = global_var.get_value('queue')
                    (uploadpath, taskid) = taskqueue.getFront()
                    taskqueue.deQueue()
                    global_var.set_value('queue', taskqueue)
                    self.getapkinfo_intoDB(uploadpath, taskid, needUpdateApkInfo=overWriteApkInfo)
            except:
                pass
            if eachTaskSleep > 0:
                time.sleep(eachTaskSleep)
            nowtime = int((time.time())*1000)
            global_var.set_value('threadBit',nowtime)
                
    def apkinfo_md5_query(self,taskid):
        querySql = 'select file_md5 from apk_task_info where task_id=%d;' % taskid
        ins_db = toolDB.Sql()
        retsql = ins_db.query(querySql)
        ins_db.closedb()
        if not retsql:
            return None
        ret = retsql
        if not ret[0][0] or ret[0][0]=='':
            return None
        return ret[0][0]
    
    def apkInfoResult_query(self, uploadpath=None, taskid=None, format=None):
        if not taskid and uploadpath:
            return self.getApkInfo_byUpload(uploadpath)
        elif not uploadpath and not taskid:
            return None
        else:
            if isinstance(taskid, str):
                taskid = int(taskid)
            taskMd5 = self.apkinfo_md5_query(taskid)
            if not taskMd5:
                return None
            querySql = "select result_json,result_html from apk_apk_info where file_md5='%s';" % taskMd5
            ins_db = toolDB.Sql()
            retsql = ins_db.query(querySql)
            ins_db.closedb()
            if not retsql:
                return None
            ret = retsql
            if not ret[0][0] or ret[0][0]=='':
                return None
            if format == 'html':
                if not ret[0][1] or ret[0][1]=='':
                    return None
                return ret[0][1]
            return ret[0][0]           

    def timestampToDatetime(self,timestamp):  # 将 unix时间戳(类型为float或整数)，转换为日期格式数字字符串
        value = int(timestamp)
        value = time.localtime(value)
        dt = time.strftime('%Y%m%d%H%M%S', value)
        return dt

    def intoStr(self, path, data):
        if path and data:
            file = open(path, "w")
            file.write(data)
            file.close

    def fromStr(self,path):
        f = open(path, "r")
        data = f.read()
        f.close()
        return data
    
    def intoBin(self,path, data):
        if path and data:
            file = open(path, "wb")
            file.write(data)
            file.close
    
    def fromBin(self,path):
        f = open(path, "rb")
        data = f.read()
        f.close()
        return data

    def reReplase(self,reg,replaseStr,content,dataDecode=False):
        if dataDecode:
            content = content.decode()
        comReg = re.compile(reg)
        m = comReg.search(content)
        if m:
            resultStr = comReg.sub(replaseStr,content)
            return resultStr
        else:
            return content
        
    def ifjson(self,teststr):
        retstr = teststr
        if isinstance(retstr, str):
            for i in range(99999):
                nReg = re.compile(r'\n')
                n = nReg.search(retstr)
                if n:
                    retstr = self.reReplase(r'\n\s+',"",retstr)
                    retstr = self.reReplase(r'\n',"",retstr)
                else:
                    break
            mReg = re.compile(r'^\{.*}$')
            m = mReg.search(retstr)
            if m:
                return True
        return False    

    def getStrJsonFormat(self,str):
        retjson = json.loads(str)
        ret = json.dumps(retjson, sort_keys=False, indent=2)
        return ret

    def jsonStr2HtmlStr(self,jsonstr): #一维json转html
        html_str = ''
        json_obj = json.loads(jsonstr)
        for key in json_obj.keys():
            html_str = html_str + '<p>%s：%s</p>' % (str(key), str(json_obj[key]))
        return html_str

    def transUrlToDict(self,url): # url 中的参数 转为字典
        try:
            result = parse.urlparse(url)
            query_dict = parse.parse_qs(result.query)
            if query_dict:
                return query_dict
            return None
        except Exception:
            return None
    
if __name__ == "__main__":
    print("done!")
