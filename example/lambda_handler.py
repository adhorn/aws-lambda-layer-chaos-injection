from chaos_lib import corrupt_delay
from chaos_lib import corrupt_exception
from chaos_lib import corrupt_statuscode
from chaos_lib import SessionWithDelay

# from chaos_lib import *


# def dummy1():
#     session = SessionWithDelay(delay=300)
#     session.get('https://stackoverflow.com/')
#     pass


# @corrupt_delay
# def dummy2():
#     pass


# @corrupt_exception
# def lambda_handler(event, context):
#     return {
#         'statusCode': 200,
#         'body': 'Hello from Lambda!'
#     }


@corrupt_delay
def lambda_handler(event, context):
    return {
        'statusCode': 200,
        'body': 'Hello from Lambda!'
    }


# @corrupt_statuscode
# def lambda_handler(event, context):
#     return {
#         'statusCode': 200,
#         'body': 'Hello from Lambda!'
#     }
