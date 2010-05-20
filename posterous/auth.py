# Copyright:
#    Copyright (c) 2010, Benjamin Reitzammer <http://github.com/nureineide>, 
#    All rights reserved.
#            
# License:
#    This program is free software. You can distribute/modify this program under
#    the terms of the Apache License Version 2.0 available at 
#    http://www.apache.org/licenses/LICENSE-2.0.txt 

from base64 import b64encode


class BasicAuthHandler(object):
    
    def __init__(self, username, password):
        self._b64auth = b64encode('%s:%s' % (username, password))

    def apply_auth(self, headers):
        headers['Authorization'] = 'Basic %s' % self._b64auth

