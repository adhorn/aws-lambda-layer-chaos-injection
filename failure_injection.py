# -*- coding: utf-8 -*-

from __future__ import division, unicode_literals

import sys
sys.path.insert(0, '/opt/python/.vendor')

from ssm_cache import SSMParameter, InvalidParameterError
import os
import time
import random
import json
import requests

logger = logging.getLogger(__name__)

__version__ = '0.3.0'



class SessionWithDelay(requests.Session):
    def __init__(self, delay=None, *args, **kwargs):
        super(SessionWithDelay, self).__init__(*args, **kwargs)
        self.delay = delay

    def request(self, method, url, **kwargs):
        print('Added {1:.2f}ms of delay to {0:s}'.format(
            method, self.delay))
        time.sleep(self.delay / 1000.0)
        return super(SessionWithDelay, self).request(method, url, **kwargs)


def get_config(config_key):
    param = SSMParameter(os.environ['FAILURE_INJECTION_PARAM'])
    try:
        value = json.loads(param.value)
        if not value["isEnabled"]:
            return 0, 1
        return value[config_key], value.get('rate', 1)
    except InvalidParameterError as e:
        # key does not exist in SSM
        raise InvalidParameterError("{} does not exist in SSM".format(e))
    except KeyError as e:
        # not a valid Key in the SSM configuration
        raise KeyError("{} is not a valid Key in the SSM configuration".format(e))


def corrupt_delay(func):
    """
    Add delay to the lambda function - delay is returned from the SSM paramater
    using get_config('delay') which returns a tuple delay, rate.

    Usage::

      >>> from failure_injection import corrupt_delay
      >>> @corrupt_delay
      ... def handler(event, context):
      ...    return {
                'statusCode': 200,
                'body': 'Hello from Lambda!'
             }
      >>>
      This will create the follow Log outup (with a delay of 400ms)
    
        START RequestId: 5295aa0b-...-50fcfbebea1f Version: $LATEST
        delay: 400, rate: 1
        Added 400.61ms to lambda_handler
        END RequestId: 5295aa0b-...-50fcfbebea1f
        REPORT RequestId: 5295aa0b-...-50fcfbebea1f Duration: 442.65 ms Billed Duration: 500 ms  Memory Size: 128 MB Max Memory Used: 79 MB

    """
    def wrapper(*args, **kwargs):
        delay, rate = get_config('delay')
        if not delay:
            return func(*args, **kwargs)
        print("delay: {0}, rate: {1}".format(delay, rate))
        # if delay and rate exist, delaying with that value at that rate
        start = time.time()
        if delay > 0 and rate >= 0:

            # add latency approx rate% of the time
            if random.random() <= rate:
                time.sleep(delay / 1000.0)

        result = func(*args, **kwargs)
        end = time.time()

        print('Added {1:.2f}ms to {0:s}'.format(
            func.__name__,
            (end - start) * 1000
        ))
        return result
    return wrapper


def corrupt_exception(func):
    """
    Forces the lambda function to fail and raise an exception
    using get_config('exception_msg') which returns a tuple exception_msg, rate.

    Usage::

      >>> from failure_injection import corrupt_exception
      >>> @corrupt_exception
      ... def handler(event, context):
      ...    return {
                'statusCode': 200,
                'body': 'Hello from Lambda!'
             }
      >>>
      This will create the follow Log outup (with a msg "I failed!")
    
    {
        "errorMessage": "I really failed seriously",
        "errorType": "Exception",
        "stackTrace": [
            "  File \"failure_injection.py\", line 76, in wrapper\n    raise Exception(exception_msg)\n"
       ]
    }
    """
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        exception_msg, rate = get_config('exception_msg')
        if not exception_msg:
            return result
        print("exception_msg from config {0} with a rate of {1}".format(exception_msg, rate))
        # add injection approx rate% of the time
        if random.random() <= rate:
            print("corrupting now")
            raise Exception(exception_msg)
        else:
            return result
    return wrapper


def corrupt_statuscode(func):
    """
    Forces the lambda function to return with a specific Status Code
    using get_config('error_code') which returns a tuple error_code, rate.

    Usage::

      >>> from failure_injection import corrupt_statuscode
      >>> @corrupt_statuscode
      ... def handler(event, context):
      ...    return {
                'statusCode': 200,
                'body': 'Hello from Lambda!'
             }
      >>> { "statusCode": 404, "body": "\"Hello from Lambda!\"" }
    """
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        error_code, rate = get_config('error_code')
        if not error_code:
            return result
        print("Error from config {0} at a rate of {1}".format(error_code, rate))
        # add injection approx rate% of the time
        if random.random() <= rate:
            print("corrupting now")
            result['statusCode'] = error_code
            return result
        else:
            return result
    return wrapper
