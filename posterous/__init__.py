# Copyright:
#    Copyright (c) 2010, Benjamin Reitzammer <http://github.com/nureineide>, 
#    All rights reserved.
#            
# License:
#    This program is free software. You can distribute/modify this program under
#    the terms of the Apache License Version 2.0 available at 
#    http://www.apache.org/licenses/LICENSE-2.0.txt 

"""
Simple wrapper-lib for accessing the Posterous API via python.
See http://posterous.com/api
"""
                            
__version__ = "0.2"
__author__ = "Benjamin Reitzammer <http://github.com/nureineide>"
__email__ = "benjamin@squeakyvessel.com"
__credits__ = ['Michael Campagnaro <http://github.com/mikecampo>']

from posterous.api import API
from posterous.auth import AuthHandler


# unauthenticated instance 
api = API()
