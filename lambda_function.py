from chaos_lib import corrupt_delay
from chaos_lib import corrupt_expection
from chaos_lib import corrupt_statuscode
from chaos_lib import SessionWithDelay



os.environ["FAILURE_INJECTION_PARAM"] = 'chaoslambda.config'


def dummy1():
    session = SessionWithDelay(delay=300)
    session.get('https://stackoverflow.com/')
    pass


@corrupt_delay
def dummy2():
    pass


@corrupt_expection
def lambda_handler_example1(event, context):
    return {
        'statusCode': 200,
        'body': 'Hello from Lambda!'
    }


@corrupt_delay
def lambda_handler_example2(event, context):
    return {
        'statusCode': 200,
        'body': 'Hello from Lambda!'
    }


@corrupt_statuscode
def lambda_handler_example3(event, context):
    return {
        'statusCode': 200,
        'body': 'Hello from Lambda!'
    }
