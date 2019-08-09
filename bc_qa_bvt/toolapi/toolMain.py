#coding:utf-8
from flask import Flask, render_template, request
from flask import make_response, send_from_directory
from werkzeug.utils import secure_filename
import time
import json
import os
import toolBase
import threading
import toolDB
import toolQueue
import global_var
import config

datains = config.basedata()
TESTMODE = datains.TESTMODE
apkInfoQueryUrl = datains.apkInfoQueryUrl

apktask_queue = toolQueue.MyQueue()
app = Flask(__name__)
ALLOWED_EXTENSIONS = set(['bin','txt','png','jpg','xls','JPG','PNG','xlsx','gif','GIF','apk'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS

@app.route('/',methods=['GET','POST'])
def home():
    a = "Welcome!"
    return '<h1>%s</h1>' % a

@app.route('/tools/',methods=['GET'])
def ende_get(body_data=None,resp_body=None,task_time_filename=None):
    return render_template('tools.html',body_data=body_data,resp_body=resp_body,task_time_filename=task_time_filename)

@app.route('/tools',methods=['POST'])
def ende_post():
    directory = os.getcwd()
    retStr = '<p>None</p>'
    encrypt_select = None
    reqmethod = None
    
    ende_select = None
    body_from_file = False
    body_from_file_path = None
    body_data_in_bin = False
    body_data_out_bin = False
    decode_type = None
    content_type = None
    timestamp = time.time()
    
    url = ""
    body_data = ""
    body_type=None
    resp_body = ""
    task_time_filename = None
    
    retContent = "render_template('tools.html',body_data=body_data,resp_body=resp_body,task_time_filename=task_time_filename)"
    ins_tool = toolBase.Tools()
    task_time = ins_tool.timestampToDatetime(timestamp)
    
    try:
        encrypt_select = request.form['multipleselect_encrypt_type[]']
    except:
        pass
    try:
        f = request.files['upload_file']
        if f:
            body_from_file = True
        basepath = os.path.dirname(__file__)
        upload_path = os.path.join(basepath, 'root/uploads',secure_filename(f.filename))
        body_from_file_path = upload_path
        f.save(upload_path)
    except:
        pass
    try:
        reqmethod = request.form['method']
    except:
        pass
    if body_from_file:
        if encrypt_select == "FileMD5": #当选择文件MD5 则计算上传文件MD5
            if not upload_path:
                resp_body = "Please upload for file MD5..."
            else:
                body_data = 'Upload file is: ' + os.path.basename(upload_path)
                resp_body = ins_tool.md5File(upload_path)
                if reqmethod == "post":
                    return resp_body
            return eval(retContent)
        if encrypt_select == "ApkInfo":
            if not upload_path:
                resp_body = "Please upload for Apk Info..."
            else:
                body_data = 'Upload file is: ' + os.path.basename(upload_path)
                resp_body = ins_tool.getApkInfo_byUpload(upload_path)
                resp_body = json.dumps(resp_body)
                if reqmethod == "post":
                    return resp_body
                if ins_tool.ifjson(resp_body) and reqmethod != "post":
                    resp_body = ins_tool.getStrJsonFormat(resp_body) #转json格式输出
            return eval(retContent)
        if '.bin' in body_from_file_path:
            body_data = ins_tool.fromBin(body_from_file_path)
            body_data_in_bin = True
        else:
            body_data = ins_tool.fromStr(body_from_file_path)
    else:
        try:
            body_data = request.form['body_data']
        except:
            pass
    try:
        ende_select = request.form['multipleselect_ende_select[]']
    except:
        pass
    try:
        ende_select = request.form['type']
    except:
        pass
    try:
        body_type = request.form['body_type']
    except:
        pass
    try:
        decode_type = request.form['decode_type']
    except:
        pass
    try:
        content_type = request.form['content_type']
    except:
        pass

    if encrypt_select == "MD5":
        resp_body = ins_tool.md5str(body_data.encode())
        return eval(retContent)
    if body_type=="MD5":
        if reqmethod == "post":
            resp_body =  ins_tool.md5str(body_data.encode())
            return resp_body
        
    if encrypt_select == "base64":
        resp_body = ins_tool.base64py(body_data.encode(), type=ende_select)
        return eval(retContent)
    if body_type=="base64":
        if reqmethod == "post":
            resp_body =  ins_tool.base64py(body_data.encode(), type=ende_select)
            return resp_body
        
    if isinstance(resp_body, str):
        task_time_filename = task_time + '.txt'
        filepath = directory + '/root/allfile/%s' % task_time_filename
        ins_tool.intoStr(filepath, resp_body)
    else:
        task_time_filename = task_time + '.bin'
        filepath = directory + '/root/allfile/%s' % task_time_filename
        ins_tool.intoBin(filepath, resp_body)
    
    if ins_tool.ifjson(body_data):
        body_data = ins_tool.getStrJsonFormat(body_data) #转json格式输出
    return eval(retContent)

@app.route("/download/", methods=['GET','POST'])
def download():
    if request.method == 'GET':
        fullfilename = request.args.get('filename')
        fullfilenamelist = fullfilename.split('/')
        filename = fullfilenamelist[-1]
        directory = os.getcwd()
        filepath = directory + '/root/allfile/'
        
        response = make_response(send_from_directory(filepath, filename, as_attachment=True))
        response.headers["Content-Disposition"] = "attachment; filename={}".format(filepath.encode().decode('latin-1'))
        return send_from_directory(filepath, filename, as_attachment=True)

@app.route('/apkinfo/upload',methods=['POST'])
def apkinfo_upload():
    ins_tool = toolBase.Tools()
    upload_path = None
    task_id = None
    body_from_file = False
    try:
        upload_path = request.form['path']
        task_id = request.form['taskid']
    except:
        pass
    
    if upload_path and not task_id:
        return '{"status": 1, "reason":"no taskid"}'
    elif not upload_path:
        try:
            f = request.files['upload_file']
            if f:
                body_from_file = True
            basepath = os.path.dirname(__file__)
            upload_path = os.path.join(basepath, 'root/uploads',secure_filename(f.filename))
            f.save(upload_path)
        except:
            pass
    else:
        body_from_file = True
    
    if body_from_file:
        if not upload_path:
            return '{"status": 1, "reason":"no uploadfiles"}'
        else:
            if not os.path.exists(upload_path):
                return '{"status": 1, "reason":"no uploadfiles"}'
            nowtime = int((time.time())*1000)
            if not task_id:
                task_id = str(nowtime)
            try:
                tb = global_var.get_value('threadBit')
            except:
                tb = nowtime
                global_var.set_value('threadBit', tb)
            if (nowtime - tb) > 30000:
                eachTaskSleep = 0.1
                overWriteApkInfo=True
                try:
                    threadName = 't_queue'
                    execStr = '%s = threading.Thread(target=ins_tool.queue_consumer, args=(eachTaskSleep,overWriteApkInfo))' % threadName
                    exec(execStr)
                    exec('%s.start()' % threadName)
                    nowtime = int((time.time())*1000)
                    global_var.set_value('threadBit',nowtime)
                except:
                    pass
            apktask_queue.enQueue((upload_path,task_id))
            global_var.set_value('queue', apktask_queue)
            returl = apkInfoQueryUrl + ('%s' % task_id)
            ret = '{"status": 0, "queryurl":"%s"}' % returl
            sqlstr = "insert into apk_task_info(task_id,status,file_md5) values (%d, %d, '');" % (int(task_id), 0)
            ins_db = toolDB.Sql()
            ins_db.update(sqlstr)
            ins_db.closedb()
            if TESTMODE:
                sqlstr = "insert into apk_apk_results(run_status,run_result,detail,task_id) values (0, 0,'',%s);" % int(task_id)
                ins_db = toolDB.Sql()
                ins_db.update(sqlstr)
                ins_db.closedb()
            return ret
    return '{"status": 1, "reason":"no uploadfiles"}'
        
@app.route('/apkinfo/query',methods=['GET'])
def apkinfo_query():
    ins_tool = toolBase.Tools()
    gettaskid = None
    try:
        gettaskid = request.args.get("taskid")
        format = request.args.get("format")
    except:
        pass
    if not gettaskid:
        return '{"status": 1, "reason":"no taskid"}'
    task_id = int(gettaskid)
    if format=='html':
        retquery = ins_tool.apkInfoResult_query(taskid=task_id,format=format)
    else:
        retquery = ins_tool.apkInfoResult_query(taskid=task_id)
    if not retquery or retquery=='':
        return '{"status": 1, "reason":"no data"}'
    return '{"status": 0, "reason":%s}' % retquery

@app.route('/virscan/upload',methods=['POST'])
def virscan():
    return 'virscan'

@app.route('/safescan/upload',methods=['POST'])
def safescan():
    return 'safescan'

@app.route('/sendemail',methods=['POST'])
def sendemail():
    return 'email'
               
if __name__ == '__main__':
    global_var._init()
    ins_tool = toolBase.Tools()
    eachTaskSleep = 0.1
    overWriteApkInfo=True
    try:
        threadName = 't_queue'
        execStr = '%s = threading.Thread(target=ins_tool.queue_consumer, args=(eachTaskSleep,overWriteApkInfo))' % threadName
        exec(execStr)
        exec('%s.start()' % threadName)
        nowtime = int((time.time())*1000)
        global_var.set_value('threadBit',nowtime)
    except:
        pass
    app.run(host='0.0.0.0', port='9019')
    #app.debug = True
