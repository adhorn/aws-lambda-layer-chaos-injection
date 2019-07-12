from setuptools import setup

import failure_injection

long_description = open('README.md').read()

setup(
    name='failure-injection',

    version=failure_injection.__version__,

    description='Decorators to inject failures into AWS Lambda handlers',
    long_description=long_description,

    author='Adrian Hornsby',
    author_email='adhorn@amazon.com',

    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 5 - Production/Stable',

        'Environment :: Other Environment',

        'Intended Audience :: Developers',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],

    keywords='chaos engineering lambda decorator aws lambda',

    py_modules=['failure-injection'],

    setup_requires=['pytest-runner'],
    install_requires=['boto3', 'jsonschema'],
    tests_require=['pytest'],
)
