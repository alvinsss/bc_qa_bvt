from django.http import JsonResponse
from apps.utils.exception.my_exception import ErrorCode

def response_json(success, error_code, message, data):
    result = dict()
    result["success"] = success
    result["error"] = {
        "code": error_code,
        "status": message
    }
    result["data"] = data
    print("result------------------",result)
    return JsonResponse(result, safe=False)


def response_success(data={}):
    return response_json(True, "", "", data)


def response_failed(code=ErrorCode.COMMON, message="参数错误"):
    return response_json(False, code, message, {})

