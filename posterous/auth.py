# Copyright:
#    Copyright (c) 2010, Benjamin Reitzammer <http://github.com/nureineide>, 
#    All rights reserved.
#            
# License:
#    This program is free software. You can distribute/modify this program under
#    the terms of the Apache License Version 2.0 available at 
#    http://www.apache.org/licenses/LICENSE-2.0.txt 

import base64


class BasicAuthHandler(object):
    
    def __init__(self, username, password):
        self.username = username
        self._b64auth = base64.b64encode('%s%s' % (username, password))

    def apply_auth(self, headers):
        headers['Authorization'] = 'Basic %s' % self._b64auth

