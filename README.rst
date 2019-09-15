
Chaos Injection Layer for AWS Lambda - chaos_lib
=============================================================

|issues| |Maintenance| |twitter|


.. |twitter| image:: https://img.shields.io/twitter/url/https/github.com/adhorn/aws-lambda-chaos-injection?style=social
    :alt: Twitter
    :target: https://twitter.com/intent/tweet?text=Wow:&url=https%3A%2F%2Fgithub.com%2Fadhorn%2Faws-lambda-chaos-injection

.. |issues| image:: https://img.shields.io/github/issues/adhorn/FailureInjectionLayer
    :alt: Issues

.. |Maintenance| image:: https://img.shields.io/badge/Maintained%3F-yes-green.svg
    :alt: Maintenance
    :target: https://GitHub.com/adhorn/FailureInjectionLayer/graphs/commit-activity


``chaos_lib`` is a small library injecting chaos into `AWS Lambda Layers
<https://docs.aws.amazon.com/lambda/latest/dg/configuration-layers.html>`_.
It offers simple python decorators to do `delay`, `exception` and `statusCode` injection
and a Class to add `delay` to any 3rd party dependencies called from your function.
This allows to conduct small chaos engineering experiments for your serverless application
in the `AWS Cloud <https://aws.amazon.com>`_.

* Support for Latency injection using ``delay``
* Support for Exception injection using ``exception_msg``
* Support for HTTP Error status code injection using ``error_code``
* Support for disk space failure injection using ``file_size`` (EXPERIMENTAL)
* Using for SSM Parameter Store to control the experiment using ``isEnabled``
* Support for adding rate of failure using ``rate``. (Default rate = 1)
* Per function control using Environment variable (``FAILURE_INJECTION_PARAM``)

Install
--------
See the full blog post describing how to install and use ``chaos_lib`` `here
<https://medium.com/@adhorn/injecting-chaos-to-aws-lambda-functions-using-lambda-layers-2963f996e0ba>`_.


Example
--------
.. code:: python

    # function.py

    import os
    from chaos_lib import (
        corrupt_delay, corrupt_exception, corrupt_statuscode, SessionWithDelay)

    os.environ['CHAOS_PARAM'] = 'chaoslambda.config'

    def session_request_with_delay():
    session = SessionWithDelay(delay=300)
    session.get('https://stackoverflow.com/')
    pass


    @corrupt_exception
    def handler_with_exception(event, context):
    return {
        'statusCode': 200,
        'body': 'Hello from Lambda!'
    }


    @corrupt_exception(exception_type=ValueError)
    def handler_with_exception_arg(event, context):
    return {
        'statusCode': 200,
        'body': 'Hello from Lambda!'
    }


    @corrupt_exception(exception_type=TypeError, exception_msg='foobar')
    def handler_with_exception_arg2(event, context):
    return {
        'statusCode': 200,
        'body': 'Hello from Lambda!'
    }


    @corrupt_statuscode
    def handler_with_statuscode(event, context):
    return {
        'statusCode': 200,
        'body': 'Hello from Lambda!'
    }


    @corrupt_statuscode(error_code=500)
    def handler_with_statuscode_arg(event, context):
    return {
        'statusCode': 200,
        'body': 'Hello from Lambda!'
    }


    @corrupt_delay
    def handler_with_delay(event, context):
    return {
        'statusCode': 200,
        'body': 'Hello from Lambda!'
    }


    @corrupt_delay(delay=1000)
    def handler_with_delay_arg(event, context):
    return {
        'statusCode': 200,
        'body': 'Hello from Lambda!'
    }


    @corrupt_delay(delay=0)
    def handler_with_delay_zero(event, context):
    return {
        'statusCode': 200,
        'body': 'Hello from Lambda!'
    }


When excecuted, the Lambda function, e.g ``handler_with_exception('foo', 'bar')``,
will produce the following result:

.. code:: shell

    exception_msg from config I really failed seriously with a rate of 1
    corrupting now
    Traceback (most recent call last):
    File "<stdin>", line 1, in <module>
    File "/.../chaos_lambda.py", line 199, in wrapper
        raise Exception(exception_msg)
    Exception: I really failed seriously

Configuration
-------------
The configuration for the failure injection is stored in the `AWS SSM Parameter Store
<https://aws.amazon.com/ssm/>`_ and accessed at runtime by the ``get_config()``
function:

.. code:: json

    {
        "isEnabled": true,
        "delay": 400,
        "error_code": 404,
        "exception_msg": "I really failed seriously",
        "rate": 1,
        "file_size": 100
    }

To store the above configuration into SSM using the `AWS CLI <https://aws.amazon.com/cli>`_ do the following:

.. code:: shell

    aws ssm put-parameter --region eu-north-1 --name chaoslambda.config --type String --overwrite --value "{ "delay": 400, "isEnabled": true, "error_code": 404, "exception_msg": "I really failed seriously", "rate": 1 }"

AWS Lambda will need to have `IAM access to SSM <https://docs.aws.amazon.com/systems-manager/latest/userguide/sysman-paramstore-access.html>`_.

.. code:: json

    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "ssm:DescribeParameters"
                ],
                "Resource": "*"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "ssm:GetParameters",
                    "ssm:GetParameter"
                ],
                "Resource": "arn:aws:ssm:eu-north-1:12345678910:parameter/chaoslambda.config"
            }
        ]
    }


Supported Decorators:
---------------------
``chaos_lambdalayer`` currently supports the following decorators:

* `@corrupt_delay` - add delay in the AWS Lambda execution
* `@corrupt_exception` - Raise an exception during the AWS Lambda execution
* `@corrupt_statuscode` - force AWS Lambda to return a specific HTTP error code
* `@corrupt_filesize` - EXPERIMENTAL force AWS Lambda to return a specific HTTP error code

    `Note that disabling the disk space failure experiment will not cleanup /tmp for you.`

and the following class:

* `SessionWithDelay` - enables calling dependencies with delay

Building and deploying:
-----------------------

1. Clone the lambda layer

  .. code:: shell

      git clone git@github.com:adhorn/LatencyInjectionLayer.git


2. Build the dependencies

Regardless if you are using Linux, Mac or Windows, the simplest way to create your ZIP package for Lambda Layer is to use Docker.
If you don't use Docker but instead build your package directly in your local environment,
you might see an ```invalid ELF header``` error while testing your Lambda function.
That's because AWS Lambda needs Linux compatible versions of libraries to execute properly.
That's where Docker comes in handy. With Docker you can very easily run a Linux container locally on your Mac, Windows and Linux computer,
install the Python libraries within the container so they're automatically in the right Linux format, and ZIP up the files ready
to upload to AWS. You'll need Docker installed first. (https://www.docker.com/products/docker).

Spin-up a docker-lambda container, and install the Python requirements in ``.vendor``

  .. code:: shell

      docker run -v $PWD:/var/task -it lambci/lambda:build-python3.6 /bin/bash -c "pip install -r python/requirements.txt -t ./python/.vendor"

The ``-v`` flag makes the local directory available inside the container in the directory called working. You should now be inside the container with a shell prompt.

3. Package your code

  .. code:: shell

      zip -r chaos_lib.zip ./python

Voila! Your package file chaos_lib.zip is ready to be used in Lambda Layer.

4. Deploy with Serverless framework

  .. code:: shell

      sls deploy
