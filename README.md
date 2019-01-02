## "Using AWS Lambda layers to inject lantency into AWS Lambda functions"

## Building the zip package on a MAC (easy on Linux)
1. If you upload the Mac version of ZIP files with PIP requirements installed with a MAC environment, you’ll see “invalid ELF header” logs when you try to test your Lambda function.
* You need Linux versions of library files to be able to run in AWS Lambda environment. That's where Docker comes in handy. 
* With Docker you can very easily can run a Linux container locally on your Mac, install the Python libraries within the container so they are automatically in the right Linux format, and zip up the files ready to upload to AWS. 
* You’ll need Docker for Mac installed first. (https://www.docker.com/products/docker)

2. Spin up an Ubuntu container which will have the lambda code you want to package
    * run the following command:

        ```
        $ docker run -v <full path directory with your code>:/working -it --rm ubuntu
        ```
        The -v flag makes your code directory available inside the container in a directory called “working”.
        You should now be inside the container at a shell prompt.

3. Install pip and zip.
    * run the following commands:    
        ```
        $ apt-get update
        $ apt-get install python-pip
        $ apt-get install zip
        ```

4. Install the python requirements.
    * run the following commands:    
        ```
        $ cd working
        $ pip install -r python/requirements.txt -t ./python/.vendor
        ```

5. Package your code.
    * run the following commands:
        ```
        $ zip -r chaos_lib.zip ./python
        ```

Voila! Your package file chaos_lib.zip is ready to be used in Lambda Layer.
