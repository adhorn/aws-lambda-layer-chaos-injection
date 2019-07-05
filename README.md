
## Injecting Chaos to AWS Lambda functions using Lambda Layers

* See the full blog post describing how to install and use this small chaos library [here](https://medium.com/@adhorn/injecting-chaos-to-aws-lambda-functions-using-lambda-layers-2963f996e0ba).

### Changes by Gunnar Grosch
Some changes made to be able to control injection per function instead of for all functions.

* Each function with the layer attached must have an environment variable named FAILURE_INJECTION_PARAM and containing the name of a parameter in Parameter Store.

* The layer can be easily installed using the serverless.yml template file using Serverless Framework: sls deploy

### Building the zip package on a MAC (easy on Linux)
* Regardless if you are using Linux, Mac or Windows, the simplest way to create your ZIP package for Lambda Layer is to use Docker. If you don't use Docker but instead build your package directly in your local environment, you might see an ```invalid ELF header``` error while testing your Lambda function. That's because AWS Lambda needs Linux compatible versions of libraries to execute properly.

* That's where Docker comes in handy. With Docker you can very easily run a Linux container locally on your Mac, Windows and Linux computer, install the Python libraries within the container so they're automatically in the right Linux format, and ZIP up the files ready to upload to AWS. You'll need Docker installed first. (https://www.docker.com/products/docker).


1. Clone the small chaos experiment library
    * run the following command:

        ```
        git clone git@github.com:adhorn/LatencyInjectionLayer.git
        ```

2. Spin-up a docker-lambda container, and install all the Python requirements in a directory call .vendor
    * run the following command:

        ```
        $ docker run -v $PWD:/var/task -it lambci/lambda:build-python3.6 /bin/bash -c "pip install -r python/requirements.txt -t ./python/.vendor"
        ```
    
    * The -v flag makes the local directory available inside the container in the directory called working. You should now be inside the container with a shell prompt.


3. Package your code.
    * run the following commands:
        ```
        $ zip -r chaos_lib.zip ./python
        ```

Voila! Your package file chaos_lib.zip is ready to be used in Lambda Layer.

4. Deploy the chaos config in paramater store.
    * run the following command:
        ```
        $ aws ssm put-parameter --region eu-north-1 --name chaoslambda.config --type String --overwrite --value "{ \"delay\": 400, \"isEnabled\": true, \"error_code\": 404, \"exception_msg\": \"I really failed seriously\" }"
        ```

