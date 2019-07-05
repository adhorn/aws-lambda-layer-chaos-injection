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

    def close(self):
        self.session.close()


def get_config(config_key):
    param = SSMParameter(os.environ['FAILURE_INJECTION_PARAM'])
    try:
        value = json.loads(param.value)
        isEnabled = value["isEnabled"]
        if not isEnabled:
            return 0
        key_ = value[config_key]
        return key_
    except InvalidParameterError as e:
        print("{} does not exist in SSM".format(e))
        raise InvalidParameterError
    except KeyError as e:
        print("{} is not a valid Key in the SSM configuration".format(e))
        raise KeyError


def corrupt_delay(func):
    def latency(*args, **kw):
        delay = get_config('delay')
        print(delay)
        start = time.time()
        # if delay exist, delaying with that value
        if delay > 0:
            time.sleep(delay / 1000.0)
        # if delay = -1 make random delays
        elif delay < 0:
            # add latency approx 50% of the time
            if random.random() > 0.5:
                # random sleep time between 1 and 10 seconds
                time.sleep(random.randint(1, 10))

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
        exception_msg = get_config('exception_msg')
        print("exception_msg from config {}".format(exception_msg))
        print("corrupting now")
        raise Exception(exception_msg)
        return result
    return wrapper


def corrupt_statuscode(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        error_code = get_config('error_code')
        print("Error from config {}".format(error_code))
        print("corrupting now")
        result['statusCode'] = error_code
        return result
    return wrapper
