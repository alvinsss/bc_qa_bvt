from django.shortcuts import render
from apk.models import APK_UPLOADFILE
from apk.models import APK_RESULTS
from django.conf import settings
from django.http import JsonResponse,HttpResponse
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from django.views.decorators.csrf import  csrf_exempt
from django.http import StreamingHttpResponse,Http404,FileResponse
from apk.timer import print_func_time
import platform
import re
import os
import time
import requests
import hashlib
from apk.AsyncHttp import AsyncHTTP
import asyncio
import socket
socket.setdefaulttimeout(10000)
import logging
log =  logging.getLogger('interface')
now = lambda: time.time()
from apps.utils.exception.my_exception import MyException
from apps.utils.http_format import response_success,response_failed
# Create your views here.
# 管理页面
# @login_required

def apk_list(request):
    apkfile_all = APK_UPLOADFILE.objects.filter(del_status=0).order_by("-create_time")
    p= Paginator(apkfile_all,15)
    page = request.GET.get('page')
    try:
        apkfile_page = p.page(page)
    except PageNotAnInteger:
        apkfile_page = p.page(1)
    log.info("apkfile_page:",apkfile_page)
    return render(request, "apk_list.html",{"apkfiles": apkfile_page , "type": "list"})


def add_apk(request):
    log.info("add apk ")
    return render(request,"apk_add.html")

def result(request,apkid):
    log.info("URL values result",apkid)
    results = APK_RESULTS.objects.filter(task_id=apkid).order_by("apk_testtype")
    p= Paginator(results,15)
    page = request.GET.get('page')
    try:
        results = p.page(page)
    except PageNotAnInteger:
        results = p.page(1)
    log.info("results_page:",results)
    return render(request,"apk_result.html",{"results":results,"type":"result"})



def detail_result(request,resultid):
    log.info("detail_apkresult",resultid)
    results = APK_RESULTS.objects.filter(id=resultid).order_by("apk_testtype")
    log.info(results)
    return render(request,"apk_detail_result.html",{"results":results,"type":"apk_detail_result"})

@csrf_exempt
def get_detail_result(request):
    '''
    后台直接返回带有html格式的字符串，包含<p>，前端以为要展示<p>，将其解析为<p>;页面不换行
    解决办法后台将<p>替换为  \n并在前端添加样式style="white-space:pre-line";
    :param request:
    :return:
    '''
    if request.method == "POST":
        id = request.POST.get("result_id", "")
        if id == "":
            return JsonResponse({"status": 10102, "message": "id不能为空"})
        else:
            #get  JSON serializable, filter 返回非JSON
            r = APK_RESULTS.objects.get( id=id )
        return JsonResponse( {"status": 10200, "message": "success", "data": r.detail.replace( '<p>', '\n' ).replace( '</p>', '' )} )


@csrf_exempt
def upload_file_page(request):
    log.info("upload_file_page ")
    return render(request,"upfile.html")

@csrf_exempt
@print_func_time
def upload_file(request):
    log.info("upload_file method!")
    if request.method == "POST":  # 请求方法为POST时，进行处理
        myFile = request.FILES.get("myfile", None)  # 获取上传的文件，如果没有文件，则默认为None
        if not myFile:
            return HttpResponse("no files for upload!")
        if (platform.system() == "Windows"): #判断当前运行程序的操作系统
            tmp_dirs = 'D:\static\lapk'
            destination = open(os.path.join( tmp_dirs, myFile.name), 'wb+')

        else:
            destination = open(os.path.join( settings.FILE_APK, myFile.name), 'wb+')
        for chunk in myFile.chunks():  # 分块写入文件
            destination.write(chunk)
        destination.close()
        return HttpResponse(myFile.name)
    else:
        return JsonResponse( {"status": 10403, "message": "请求方式只支持post"} )


@csrf_exempt
@print_func_time
def save_uploadapkfile(request):
    t0 = time.clock()
    if request.method == "GET":
        return render(request,"apk_list.html")

    if request.method == "POST":
        # 模块获取不到默认取值1
        module_id  = request.POST.get( "module_id", "1" )
        name_des   = request.POST.get("name_des","")
        uploadfile = request.FILES.get("file_obj",None)    # 获取上传的文件，如果没有文件，则默认为None
        tfid       = request.POST.get("tfid","")           # tfid  是空，认为是创建
        apk_testtype = request.POST.getlist("apk_testtype","")
        userid     = request.user.id
        username   = request.user
        log.info( "name_des--------------------->", name_des)
        log.info( "uploadfile--------------------->", uploadfile)
        log.info( "tfid--------------------->", tfid)
        log.info( "apk_testtype--------------------->", apk_testtype)

        if (platform.system() == "Windows"): #判断当前运行程序的操作系统
            tmp_dirs = 'D:\static\lapk'
            tmp_dir = os.path.join( tmp_dirs, str( username ),
                                    str( time.strftime( "%Y-%m-%d_%H%M%S", time.localtime() ) ) )
        else:
            tmp_dir = os.path.join( settings.FILE_APK, str( username ),str( time.strftime( "%Y-%m-%d_%H:%M:%S", time.localtime() ) ) )

        if not os.path.exists( tmp_dir ):
            log.info( "tmp_dir--------------------->", tmp_dir )
            log.info( tmp_dir + " dir not exists ,create dir is starting" )
            log.warning(tmp_dir + " dir not exists ,create dir is starting")
            os.makedirs( tmp_dir )
            log.info( tmp_dir + " dir not exists ,create dir is over" )
            log.warning(tmp_dir + " dir not exists ,create dir is over")
        # 新建tfid是空
        if tfid == "":
            if not uploadfile:
                log.error(uploadfile +"上传文件不存在！")
                return JsonResponse( {"status": 10401, "message": "上传文件不存在！"} )
            if uploadfile.name.split( '.' )[-1] not in ['apk']:
                log.error(uploadfile +"上传文件类型错误！")
                return JsonResponse( {"status": 10402, "message": "上传文件类型错误！"} )
            if ( ( uploadfile.name.find( '()' ) >= 0) or ( '(' in uploadfile.name ) or ( ')' in uploadfile.name ) ):
                log.error(uploadfile +"上传文件名包含'()',请重新选择！")
                return JsonResponse( {"status": 10405, "message": "上传文件名包含'()',请重新选择！"} )

            FilePathName = os.path.join( tmp_dir, uploadfile.name )
            try:
                log.info( "write uploadfile--------------------->", uploadfile )
                log.info( "write FilePathName--------------------->", FilePathName )
                with open( FilePathName, 'wb+' ) as f:
                    # 分块写入文件
                    for chunk in uploadfile.chunks():
                        f.write( chunk )

                    # APK_UPLOADFILE保存上传数据
                    log.info("FilePathName",FilePathName)
                    m5=_get_md5_value(FilePathName)
                    info_dic = _getApkInfo_byUpload(FilePathName)
                    if info_dic:
                        applicationname = info_dic['applicationName'][0]
                        apksize = str(round((int(info_dic['apkSize']) / 1000000),2 ))
                        packagename = info_dic['packageName']

                    if  userid == None  :
                        APK_UPLOADFILE.objects.create(module_id=module_id,userid="9999",username="AnonyUser",name_des=name_des,upfilepath=FilePathName,
                                                      apk_testtype=apk_testtype,md5=(_get_md5_value(FilePathName)),apksize=apksize,applicationname=applicationname,packagename=packagename )
                    else:
                        log.info( "userid is has values--------------------->", userid,username )
                        APK_UPLOADFILE.objects.create( userid=userid,module_id=module_id,username=username,
                                                       name_des=name_des,upfilepath=FilePathName,
                                                       apk_testtype=apk_testtype ,md5=(_get_md5_value(FilePathName)))

                    #上传文件是zip的格式处理
                    if uploadfile.name.split( '.' )[-1] in ['zip']:
                        cmdinfo = 'unzip'+' '+FilePathName+' '+'-d'+' '+tmp_dir
                        log.info("zip cmdinfo--------------------->",cmdinfo)
                        os.system(cmdinfo)
                        time.sleep(2)
                        log.info("-----upload files type is zip, start unzip file-----")
                        apk_fileslist =_get_apkpath(tmp_dir)
                        log.info("apk_fileslist--------------------->",apk_fileslist)
                        id_list_maxid = APK_UPLOADFILE.objects.values_list('id',flat=True).last()
                        testtype_list = APK_UPLOADFILE.objects.get(id=id_list_maxid).apk_testtype[2:-2].split(',')
                        if  userid == None  :
                            for type_test in testtype_list:
                                for files in apk_fileslist:
                                    APK_RESULTS.objects.create( userid="9999",username="AnonyUser",name_des=name_des,apk_testtype=type_test,upfilepath=FilePathName,apkfile_path=files,task_id=id_list_maxid,module_id=module_id )
                        else:
                            for type_test in testtype_list:
                                for files in apk_fileslist:
                                    APK_RESULTS.objects.create( userid=userid,username=username,name_des=name_des, apk_testtype=type_test,
                                                                upfilepath=FilePathName,apkfile_path=files,task_id=id_list_maxid,module_id=module_id )
                    # 上传文件不是zip的格式处理
                    else:
                        # values_list方法加个参数flat = True可以获取number的值列表。
                        apk_fileslist =_get_apkpath(tmp_dir)
                        log.info("-----upload files type is apk----------")
                        id_list_maxid = APK_UPLOADFILE.objects.values_list('id',flat=True).last()
                        testtype_list = APK_UPLOADFILE.objects.get(id=id_list_maxid).apk_testtype[2:-2].split(',')
                        if  userid == None  :
                            for type_test in testtype_list:
                                for files in apk_fileslist:
                                    APK_RESULTS.objects.create( userid="9999",username="AnonyUser",name_des=name_des,apk_testtype=type_test,upfilepath=FilePathName,apkfile_path=files,task_id=id_list_maxid,module_id=module_id )
                        else:
                            for type_test in testtype_list:
                                for files in apk_fileslist:
                                    APK_RESULTS.objects.create( userid=userid,username=username,name_des=name_des,apk_testtype=type_test,upfilepath=FilePathName,apkfile_path=files,task_id=id_list_maxid,module_id=module_id )

                        # 增加上传文件之后运行测试
                        flag = _run_apk_taskbyupload(int(APK_UPLOADFILE.objects.values_list('id',flat=True).last()))

                        # 增加上传文件之后异步运行测试开始
                        # data = {
                        #     "taskid": int(APK_UPLOADFILE.objects.values_list('id',flat=True).last()),
                        #     "path": str( APK_UPLOADFILE.objects.get( id=int(APK_UPLOADFILE.objects.values_list('id',flat=True).last()) ).upfilepath )
                        #       # 当不支持zip的格式直接读此数据即可
                        # }
                        # flag = _run_http_async( testtype_list, data )
                        # run_info = APK_UPLOADFILE.objects.get( id=int(APK_UPLOADFILE.objects.values_list('id',flat=True).last()) )
                        # # run_info.sum_status =1 先修改成已完成 方便发邮件按钮展示
                        # run_info.sum_status = 2
                        # run_info.save()
                        # 增加上传文件之后异步运行测试结束
                        t1 = time.clock()
                        log.info( "Total running time: %s s" % (str( t1 - t0 )) )
                        if flag:
                            return JsonResponse( {"status": 10200, "message": "运行测试成功" } )
                        else:
                            return JsonResponse( {"status": 10200, "message": "运行测试失败" } )

            except Exception as e:
                    log.info( e )
            return JsonResponse( {"status": 10200, "message": "上传成功！", "data": FilePathName} )

        # uploadfile实现多态
        else:
            if uploadfile == None:
                log.info("修改，未修改上传文件",uploadfile)
                apk_uploadinfo = APK_UPLOADFILE.objects.get( id=tfid )
                apk_uploadinfo.userid = userid
                apk_uploadinfo.name_des = name_des
                apk_uploadinfo.apk_testtype = apk_testtype
                apk_uploadinfo.save()
                return JsonResponse( {"status": 10200, "message": "修改成功！", "data": apk_uploadinfo.name_des} )
            else:
                log.info("修改上传文件",uploadfile)
                FilePathName = os.path.join( tmp_dir, uploadfile.name )
                try:
                    with open( FilePathName, 'wb+' ) as f:
                        # 分块写入文件
                        for chunk in uploadfile.chunks():
                            f.write( chunk )
                    apk_uploadinfo = APK_UPLOADFILE.objects.get( id=tfid )
                    apk_uploadinfo.userid = userid
                    apk_uploadinfo.name_des = name_des
                    apk_uploadinfo.apk_testtype = apk_testtype
                    apk_uploadinfo.upapkfile = FilePathName
                    apk_uploadinfo.save()
                except Exception as e:
                    log.info( e )
                return JsonResponse( {"status":10200, "message": "修改成功！", "data": FilePathName} )

        return render(request,"apk_add.html")

def _getApkInfo_byUpload(uploadpath):
    '''
    获取 packagename  versionCode  versionName apk_size
    :param uploadpath:
    :return:
    '''
    info = {}
    if (platform.system() == "Windows"): #判断当前运行程序的操作系统
        # log.info("settings.BASE_DIR",settings.BASE_DIR)
        # path = r"D:\UserData\git\baice\bvt\bc_qa_bvt\toolapi\tools\forapk"
        path = r"D:\UserData\git\baice\bvt\bc_qa_bvt\toolapi\tools\forapk"
        log.info("Windows path",path)
    else:
        path = settings.AAPTTOOLS
    # path = aaptpath
    aapt_path = path + "aapt"
    get_info_command = "%s dump badging %s" % (aapt_path, uploadpath)
    output = os.popen( get_info_command ).read()
    log.info("output----------->",output)

    match = re.compile( "package: name='(\S+)' versionCode='(\d+)' versionName='(\S+)'" ).match( output )
    if not match:
        return None
    info["packageName"] = match.group( 1 )
    info["versionCode"] = match.group( 2 )
    info["versionName"] = match.group( 3 )

    match_application = re.findall('application-label-zh-CN:\'(.*?)\'',output)
    if not match_application:
            return None
    info["applicationName"] = match_application
    filesize = os.path.getsize( uploadpath )
    if filesize:
        info["apkSize"] = filesize
    return info


@csrf_exempt
def download_apkfile(request,apkid):
    '''
    1.使用了django的StreamingHttpResponse对象，以文件流的方式下载文件；
    2.使用了迭代器(_file_iter()方法),将文件进行分割，避免消耗过多内存；
    3.添加响应头:Content-Type 和 Content-Disposition，让文件流写入硬盘
    HttpResponse会直接使用迭代器对象，将迭代器对象的内容存储城字符串，然后返回给客户端，同时释放内存。可以当文件变大看出这是一个非常耗费时间和内存的过程。
而StreamingHttpResponse是将文件内容进行流式传输，数据量大可以用这个方法
    :param request:
    :return:
    '''
    if request.method == "GET":
        log.info("download_apkfile apkid:",apkid)
        #apkid从URL获取，urls.py定义
        if apkid == "":
            return JsonResponse({"status":10406, "message": "id不能为空"})
        file_name = APK_UPLOADFILE.objects.get(id=apkid).upfilepath
        if file_name :
            log.info( "file_name download file", file_name )
            # 文件是否存在判断
            if not os.path.exists(str(file_name) ):
                raise Http404
            #下载文件的类型判断
            ext = os.path.basename(str(file_name)).split('.')[-1].lower()
            if ext not in ['py','db']:
                try:
                    response = StreamingHttpResponse(_file_iter(file_name))
                    log.info("response",response)
                    response['Content-Type']        = 'application/octet-stream'
                    #只取文件名，不需要file_name全路径
                    response['Content-Disposition'] = 'attachment;filename="{0}"'.format(os.path.basename(str(file_name)))
                    return response
                except Exception as e:
                    return JsonResponse( {"status": 10506, "message": "服务器没有此文件！"} )
            else:
                return JsonResponse( {"status": 10405, "message": "您下载的文件类型错误！"} )
        else:
            return JsonResponse( {"status": 10507, "message": "需要下载的文件不存在！"} )
    else:
        return JsonResponse( {"status": 10400, "message": "请求方式只支持post"} )


@csrf_exempt
def send_apk_mail(request):
    if request.method == "POST":
        tid = request.POST.get("task_id","")
        if tid == "":
            return JsonResponse({"status": 10102, "message": "id不能为空"})
        url = settings.APK_SEND_MAIL+tid
        r = requests.get(url)
        log.info("send_apk_mail URL is %s , text is %s "%(url,r.text) )
        if (r.status_code) == 200:
            return JsonResponse( {"status": 10200, "message": "发送邮件成功"} )
        else:
            return JsonResponse( {"status": 10103, "message": "发送邮件失败"} )



def _get_md5_value(file_path):
    md5 = None
    if os.path.isfile(file_path):
        f = open(file_path,'rb')
        md5_obj = hashlib.md5()
        md5_obj.update(f.read())
        hash_code = md5_obj.hexdigest()
        f.close()
        md5 = str(hash_code).lower()
        log.info("file_path:%s md5-value:%s"%(file_path,md5))
    return md5

def _file_iter(file_name,chunk_size=512):
    log.info("_file_iter .....",file_name)
    with open(str(file_name),'rb') as f:
        while True:
            c = f.read(chunk_size)
            if c:
                yield c
            else:
                break

def _get_md5_bigfile(file_path):
    '''
    大文件获取md5操作
    :param file_path:
    :return:
    '''
    f = open( file_path, 'rb' )
    md5_obj = hashlib.md5()
    while True:
        d = f.read( 8096 )
        if not d:
            break
        md5_obj.update( d )
    hash_code = md5_obj.hexdigest()
    f.close()
    md5 = str( hash_code ).lower()
    return md5

@csrf_exempt
@print_func_time
def _run_apk_taskbyupload(taskid):
    data = {
            "taskid": taskid,
            "path": str( APK_UPLOADFILE.objects.get(id=taskid).upfilepath )  #当不支持zip的格式直接读此数据即可
    }
    testtype_list = APK_UPLOADFILE.objects.get( id=taskid ).apk_testtype[2:-2].split( ',' )
    log.info("_run_apk_taskbyupload data",data)
    log.info("_run_apk_taskbyupload",testtype_list)
    res_results = {}
    for type_test in testtype_list:
        log.info("type_test",type_test)
        if type_test == 'Apkinfo':
            r_apkinfo = requests.post( settings.APKINFO_URL, data )
            log.info("Apkinfo请求URL",settings.APKINFO_URL)
            log.info("Apkinfo请求数据",data)
            log.info("r_apkinfo 返回status:",r_apkinfo.status_code)
            log.info("r_apkinfo 返回text:",r_apkinfo.text)
            res_results["Apkinfo"]=int(r_apkinfo.status_code)
        elif type_test == 'VirusScanning':
            r_vs = requests.post( settings.VS_URL, data )
            log.info("VirusScanning请求URL",settings.VS_URL)
            log.info("VirusScanning请求数据",data)
            log.info("r_vs 返回status:",r_vs.status_code)
            log.info("r_vs 返回text:",r_vs.text)
            # res_results={"VirusScanning":int(r_vs.status_code)}
            res_results["VirusScanning"]=int(r_vs.status_code)
        else :
            headers = {'Content-Type':'application/json'}
            r_monkey = requests.post( url= settings.MONKEY_URL, json=data,headers=headers)
            log.info("请求URL",settings.MONKEY_URL)
            log.info("请求数据",data)
            log.info("r_monkey 返回status:",r_monkey.status_code)
            log.info("r_monkey 返回text:",r_monkey.text)
            # res_results={"Monkey":int(r_monkey.status_code)}
            res_results["Monkey"]=int(r_monkey.status_code)

    len = 0
    scuess = 0
    for status in res_results.values():
        len+=1
        if status == 200:
            scuess+=1

    if  len == scuess:
        log.info("_run_apk_taskbyupload update sum_status = 2")
        run_info = APK_UPLOADFILE.objects.get(id=taskid)
        # run_info.sum_status =1 先修改成已完成 方便发邮件按钮展示
        run_info.sum_status =2
        run_info.save()
        return True
    else:
        return False

#
# @csrf_exempt
# def _run_apk_async_taskbyupload(taskid):
#     data = {
#             "taskid": taskid,
#             "path": str( APK_UPLOADFILE.objects.get(id=taskid).upfilepath )  #当不支持zip的格式直接读此数据即可
#     }
#     res = _run_http_async( testtype_list, data )


@csrf_exempt
def run_apk_task(request):
    if request.method == "POST":
        tid = request.POST.get("tid","")
        if tid == "":
            return JsonResponse({"status":10406, "message": "id不能为空"})
        testtype_list = APK_UPLOADFILE.objects.get( id=tid ).apk_testtype[2:-2].split( ',' )
        data = {
            "taskid": tid,
            "path": str( APK_UPLOADFILE.objects.get(id=tid).upfilepath )  #当不支持zip的格式直接读此数据即可
        }
        log.info("run_apk_task  data",data)
        log.info("run_apk_task  testtype_list",testtype_list)
        res_results = {}
        for type_test in testtype_list:
            log.info("type_test",type_test)
            if type_test == 'Apkinfo':
                r_apkinfo = requests.post( settings.APKINFO_URL, data )
                log.info("Apkinfo请求URL",settings.APKINFO_URL)
                log.info("Apkinfo请求数据",data)
                log.info("r_apkinfo 返回status:",r_apkinfo.status_code)
                log.info("r_apkinfo 返回text:",r_apkinfo.text)
                res_results["Apkinfo"]=int(r_apkinfo.status_code)
            elif type_test == 'VirusScanning':
                r_vs = requests.post( settings.VS_URL, data )
                log.info("VirusScanning请求URL",settings.VS_URL)
                log.info("VirusScanning请求数据",data)
                log.info("r_vs 返回status:",r_vs.status_code)
                log.info("r_vs 返回text:",r_vs.text)
                # res_results={"VirusScanning":int(r_vs.status_code)}
                res_results["VirusScanning"]=int(r_vs.status_code)
            else :
                headers = {'Content-Type':'application/json'}
                r_monkey = requests.post( url= settings.MONKEY_URL, json=data,headers=headers)
                log.info("请求URL",settings.MONKEY_URL)
                log.info("请求数据",data)
                log.info("r_monkey 返回status:",r_monkey.status_code)
                log.info("r_monkey 返回text:",r_monkey.text)
                # res_results={"Monkey":int(r_monkey.status_code)}
                res_results["Monkey"]=int(r_monkey.status_code)

        len = 0
        scuess = 0
        for status in res_results.values():
            len+=1
            if status == 200:
                scuess+=1
        log.info(len,scuess)

        if  len == scuess:
            run_info = APK_UPLOADFILE.objects.get(id=tid)
            # run_info.sum_status =1 先修改成已完成 方便发邮件按钮展示
            run_info.sum_status =2
            run_info.save()
            return JsonResponse( {"status":10200, "message": "任务运行请求成功"} )
        else:
            return JsonResponse( {"status":10200, "message": "任务运行请求失败"} )
    else:
        return JsonResponse( {"status": 10400, "message": "请求方式只支持post"} )


@csrf_exempt
def run_apk_task_async(request):
    if request.method == "POST":
        tid = request.POST.get("tid","")
        if tid == "":
            return JsonResponse({"status":10406, "message": "id不能为空"})
        testtype_list = APK_UPLOADFILE.objects.get( id=tid ).apk_testtype[2:-2].split( ',' )
        data = {
            "taskid": tid,
            "path": str( APK_UPLOADFILE.objects.get(id=tid).upfilepath )  #当不支持zip的格式直接读此数据即可
        }
        log.info("run_apk_task_async data",data)
        log.info("run_apk_task_async testtype_list",testtype_list)
        res = _run_http_async(testtype_list,data)
        log.info("run_apk_task_async res ",res)
        if res :
            log.info("_run_http_async testtype_list")
            return JsonResponse( {"status":10200, "message": "执行中..."} )
        else:
            return JsonResponse( {"status":10200, "message": "有执行失败的任务，请注意！"} )
    else:
        return JsonResponse( {"status": 10400, "message": "请求方式只支持post"} )

def _run_http_async(testtype_list,req_data):
    start = now()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop( loop )
    tasks = []
    for type_test in testtype_list:
        log.info( "type_test _run_http_async ", type_test )
        if type_test == 'Monkey':
            log.info("_run_http_async post_json  Monkey ")
            tasks = [asyncio.ensure_future( AsyncHTTP.post_json( settings.MONKEY_URL,req_data ) )]
        elif type_test == 'VirusScanning':
            log.info("_run_http_async VirusScanning ")
            tasks = [asyncio.ensure_future( AsyncHTTP.post_text_plain( settings.VS_URL,req_data ) )]
        else:
            log.info("_run_http_async Apkinfo ")
            # tasks = [asyncio.ensure_future(AsyncHTTP.post('http://httpbin.org/post', data = {'key':'value'}))]
            tasks = [asyncio.ensure_future( AsyncHTTP.post_text_plain( settings.APKINFO_URL,req_data ) )]
    #将协程注册到事件循环，并启动事件循环
    #loop.run_until_complete(asyncio.gather(*tasks))
    # log.info("get tasks leng:",len(tasks))
    loop.run_until_complete(asyncio.wait(tasks))

    scuess_count = 0
    for task in tasks:
        # log.info("_run_http_async Task -------------->",task)
        log.info('_run_http_async Task ret--------------> ', task.result())
        if len(task.result()):
            scuess_count+=1
    # log.info("scuess_count",scuess_count)
    # log.info("testtype_list_count",len(testtype_list))
    # if scuess_count == len(testtype_list):
    #     return  True
    log.info('_run_http_async TIME: ', now() - start)
    return True


@csrf_exempt
def send_apk_mail(request):
    if request.method == "POST":
        tid = request.POST.get("task_id","")
        if tid == "":
            return JsonResponse({"status": 10102, "message": "id不能为空"})
        url = settings.APK_SEND_MAIL+tid
        r = requests.get(url)
        log.info("send_apk_mail URL is %s , text is %s "%(url,r.text) )
        if (r.status_code) == 200:
            return JsonResponse( {"status": 10200, "message": "发送邮件成功"} )
        else:
            return JsonResponse( {"status": 10103, "message": "发送邮件失败"} )

def _get_apkpath(dirname):
    filter = [".apk"]#需要获取的文件类型
    result=[]
    for maindir,subdir,file_name_list in os.walk(dirname):
        for FilePathName in file_name_list:
            apath = os.path.join(maindir,FilePathName)
            ext = os.path.splitext(apath)[1]# 获取文件后缀 [0]获取的是除了文件名以外的内容
            if ext in filter:
                result.append(apath)
    return result
