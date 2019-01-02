from local_settings import environment
from chaos_lib import delayit
from chaos_lib import SessionWithDelay


def dummy2():
    session = SessionWithDelay(delay=300)
    session.get('https://stackoverflow.com/')
    pass


@delayit
def dummy():
    pass


def lambda_handler(event, context):
    dummy()
    dummy2()
    return {
        'statusCode': 200,
        'body': 'Hello from Lambda!'
    }
