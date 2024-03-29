

class ErrorCode:
    SYSTEM = 10000
    DB = 20000
    COMMON = 30000
    UNKNOWN = 40000


class MyException(Exception):
    def __init__(self, code=ErrorCode.COMMON, message='参数错误'):
        self.message = message
        self.code = code

    def __str__(self):
        return self.message
