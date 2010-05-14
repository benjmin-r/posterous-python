#!/usr/bin/env python
#from distutils.core import setup
from setuptools import setup, find_packages

setup(
    name="posterous-python",
    version="0.1",
    description="Posterous API library for python",
    author="Benjamin Reitzammer",
    author_email="",
    url="http://github.com/nureineide/posterous-python",
    license="http://www.apache.org/licenses/LICENSE-2.0",
    packages = find_packages(),
    keywords= "posterous api library")
