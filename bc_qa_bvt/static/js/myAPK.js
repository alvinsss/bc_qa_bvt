
//获取APKFileInit信息
var APKFileInit = function () {

    var url = document.location;
    var tid =  url.pathname.split("/")[3];
    $.post("/sdk/get_sdk_info/",
    {
        task_id: tid,
    },
    function (resp, status) {

        console.log("返回的结果", resp.data);
        var result = resp.data;
        document.querySelector("#name_des").value = result.name_des;
        // alert( result.uploadfile)
        // 初始化菜单
        SelectInit(result.project_id, result.module_id);
    });

}
	//运行apktest方法
	function RunAPKtest(tid) {
		console.log("运行任务的 run_apk_task id", tid);

		$.post("/apk/run_apk_task/",
		{
			tid:tid,
		},
		function (data, status) {
			alert("提示：" + data.message);
		});
	};

	//发送email方法
    function RunAPKmail(tid) {
		console.log("运行任务的 send_apk_mail id", tid);
		$.post("/apk/send_apk_mail/",
		{
			task_id:tid,
		},
		function (data, status) {
			alert("提示：" + data.message);
		});
	};





        // {## ajax处理form表单数据#}
