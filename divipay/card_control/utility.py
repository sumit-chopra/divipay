from enum import IntEnum

def create_success_response(message, data = None):
    return __api_response(APIStatus.Success, message, data)
    
def create_fail_response(message, data = None):
    return __api_response(APIStatus.Fail, message, data)

class APIStatus(IntEnum):
    Success = 0
    Fail = 1
    
def __api_response(status, message, data):
    content = {
        "status" : status.name,
        "message" : message
    }
    if data is not None:
        content["data"] = data
    return content