
## Injecting Chaos to AWS Lambda functions using Lambda Layers

* See the full blog post describing how to install and use this small chaos library [here](https://medium.com/@adhorn/injecting-chaos-to-aws-lambda-functions-using-lambda-layers-2963f996e0ba).

### Features
* Support for Latency injection using ```delay```
* Support for Exception injection using ```exception_msg```
* Support for HTTP Error status code injection using ```error_code```
* Support for disk space failure injection using ```file_size```
* Using for SSM Parameter Store to control the experiment using ```isEnabled```
* Per Lambda function injection control using Environment variable (```FAILURE_INJECTION_PARAM```) (thanks to Gunnar Grosch)
* Support for Serverless Framework using ```sls deploy``` (thanks to Gunnar Grosch)
* Support for adding rate of failure using ```rate```. (Default rate = 1)

### Parameter Store Object
```json
{ 
    "delay": 200,
    "isEnabled": true,
    "error_code": 404,
    "exception_msg": "I FAILED",
    "file_size": 100,
    "rate": 0.5
}
```
Deploy the chaos config in paramater store.
* run the following command:
    ```
    $ aws ssm put-parameter --region eu-north-1 --name chaoslambda.config --type String --overwrite --value "{ \"delay\": 400, \"isEnabled\": true, \"error_code\": 404, \"exception_msg\": \"I really failed seriously\", \"file_size\": 100, \"rate\": 1 }"
    ```

### Building and deploying

1. Clone the small chaos experiment library
    * run the following command:

        ```
        git clone git@github.com:adhorn/LatencyInjectionLayer.git
        ```



2. Build the package manually (skip to step 4 if you want to use the serverless framework)

   Regardless if you are using Linux, Mac or Windows, the simplest way to create your ZIP package for Lambda Layer is to use Docker. If you don't use Docker but instead build your package directly in your local environment, you might see an ```invalid ELF header``` error while testing your Lambda function. That's because AWS Lambda needs Linux compatible versions of libraries to execute properly. That's where Docker comes in handy. With Docker you can very easily run a Linux container locally on your Mac, Windows and Linux computer, install the Python libraries within the container so they're automatically in the right Linux format, and ZIP up the files ready to upload to AWS. You'll need Docker installed first. (https://www.docker.com/products/docker).

-  Spin-up a docker-lambda container, and install all the Python requirements in a directory call .vendor
    * run the following command:

        ```
        $ docker run -v $PWD:/var/task -it lambci/lambda:build-python3.6 /bin/bash -c "pip install -r python/requirements.txt -t ./python/.vendor"
        ```
    
    * The -v flag makes the local directory available inside the container in the directory called working. You should now be inside the container with a shell prompt.


3. Package your code 
    * run the following commands:
        ```
        $ zip -r chaos_lib.zip ./python
        ```

        Voila! Your package file chaos_lib.zip is ready to be used in Lambda Layer.

4. Deploy with Serverless framework
    * run the following command:
        ```
        sls deploy
        ```

5. Use the (python) method decorators to inject the failure to functions (either the whole Lambda handler or any other functions).
* For latency injection, use
```python
    @corrupt_delay
``` 
* For exception injection, use
```python
    @corrupt_exception
```

* For HTTP error status code injection, use
```python
    @corrupt_statuscode
```

* For disk space failure injection, use
```python
    @corrupt_diskspace
```
Note that disabling the disk space failure experiment will not cleanup /tmp for you. One way of doing this is by updating the configuration (timeout value or env vars) of you Lambda function so that a new instance is deployd:
```
    aws lambda update-function-configuration --function-name YOUR_FUNCTION_NAME --timeout 6
```


## Happy breaking!
