from __future__ import division, unicode_literals

import sys
sys.path.insert(0, '/opt/python/.vendor')

from ssm_cache import SSMParameter, InvalidParameterError
import os
import time
import random
import json
import requests


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
            return 0
        return value[config_key], value.get('rate', 0)
    except InvalidParameterError as e:
        # key does not exist in SSM
        raise InvalidParameterError("{} does not exist in SSM".format(e))
    except KeyError as e:
        # not a valid Key in the SSM configuration
        raise KeyError("{} is not a valid Key in the SSM configuration".format(e))


def corrupt_delay(func):
    def latency(*args, **kw):
        delay, rate = get_config('delay')
        print("delay: {0}, rate: {1}".format(delay, rate))
        start = time.time()
        # if delay and rate exist, delaying with that value at that rate
        if delay > 0 and rate >= 0:
            # add latency approx rate% of the time
            if random.random() <= rate:
                time.sleep(delay / 1000.0)

        result = func(*args, **kw)
        end = time.time()

        print('Added {1:.2f}ms to {0:s}'.format(
            func.__name__,
            (end - start) * 1000
        ))
        return result
    return latency


def corrupt_expection(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        exception_msg, rate = get_config('exception_msg')
        print("exception_msg from config {0} with a rate of {1}".format(exception_msg, rate))
        # add injection approx rate% of the time
        if random.random() <= rate:
            print("corrupting now")
            raise Exception(exception_msg)
        else:
            return result
    return wrapper


def corrupt_statuscode(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        error_code, rate = get_config('error_code')
        print("Error from config {0} at a rate of {1}".format(error_code, rate))
        # add injection approx rate% of the time
        if random.random() <= rate:
            print("corrupting now")
            result['statusCode'] = error_code
            return result
        else:
            return result
    return wrapper
