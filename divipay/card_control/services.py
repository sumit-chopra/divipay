from enum import Enum
import requests
import logging
from . import errors

logger = logging.getLogger(__name__)

class HTTPMethod(Enum):
    GET = 1
    POST = 2

def get_service(url, headers):
    return api_service(HTTPMethod.GET, url, headers)

def post_service(url, headers, body = None):
    return api_service(HTTPMethod.POST, url, headers, body)

# Generic service method to hit any third party API
# defines common timeout
# Collects response and returns back    
def api_service(httpMethod, url, headers, body = None):
    try:
        logger.info("Hitting third party API {0} {1} {2} {3}".format(httpMethod, url, headers, body))
        if httpMethod == HTTPMethod.GET:
            response = requests.get(url, headers = headers, timeout = 5)
        else:
            if body is None:
                response = requests.post(url, headers = headers, timeout = 5)
            else:
                response = requests.post(url, json = body, headers = headers, timeout = 5)
        response.raise_for_status()
        logger.info("Success Response from third party {0}".format(response.status_code))
        return {
            "status" : response.status_code,
            "content" : response.json()
        }
    except (requests.ConnectionError, requests.Timeout) as e:
        logger.error("Error encountered while getting response - Unable to connect to server")
        raise errors.Unavailable() from e
    except requests.exceptions.HTTPError as e:
        logger.error("Error encountered while getting response {}".format(e.response.status_code))
        raise errors.DiviPayError(e.response.status_code, e.response.message)