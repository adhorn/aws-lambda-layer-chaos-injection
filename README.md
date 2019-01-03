## "Using AWS Lambda layers to inject lantency into AWS Lambda functions"

## Building the zip package on a MAC (easy on Linux)
* If you use Linux, please skip directly to the section (4) below: Install the Python the requirements. 
* If, like me,  you use a Mac to do your development work, the simplest way to create your ZIP package for Lambda Layer is to use Docker. If you don't use Docker but instead build your package directly in your Mac environment, you might see an invalid ELF header error while testing your Lambda function. That's because AWS Lambda needs Linux compatible versions of libraries to execute properly.

* That's where Docker comes in handy; with Docker you can very easily run a Linux container locally on your Mac, install the Python libraries within the container so they are automatically in the right Linux format, and ZIP up the files ready to upload to AWS. You'll need Docker for Mac installed first. (https://www.docker.com/products/docker). Once you have installed Docker for Mac, you can do the following:

1. Clone my small chaos experiment library
    * run the following command:

        ```
        git clone git@github.com:adhorn/LatencyInjectionLayer.git
        ```

2. Spin up an Ubuntu container which will have the lambda code you want to package
    * run the following command:

        ```
        $ docker run -v <full path directory with your code>:/working -it --rm ubuntu
        ```
    * The -v flag makes the local directory available inside the container in the directory called working. You should now be inside the container with a shell prompt.


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
    * Notice  that this command will install the dependencies inside a folder called .vendor. This is my personal preference since I like to keep the code well-organized. You can also install the python requirements directly inside the python directory thus avoiding the sys.path.insert(0, '/opt/python/.vendor') statement in chaos_lib.py (line 4).

5. Package your code.
    * run the following commands:
        ```
        $ zip -r chaos_lib.zip ./python
        ```

Voila! Your package file chaos_lib.zip is ready to be used in Lambda Layer.
