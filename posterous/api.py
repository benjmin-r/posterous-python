# Copyright:
#    Copyright (c) 2010, Benjamin Reitzammer <http://github.com/nureineide>, 
#    All rights reserved.
#            
# License:
#    This program is free software. You can distribute/modify this program under
#    the terms of the Apache License Version 2.0 available at 
#    http://www.apache.org/licenses/LICENSE-2.0.txt 

from base64 import b64encode
from copy import copy
import xml.parsers.expat
import logging 
import os.path
from datetime import datetime, timedelta
import urllib2, urllib

from posterous.bind import bind_method
from posterous.utils import *


class API(object):
    def __init__(self, auth_handler=None, host='posterous.com',
                 api_root='/api', parser=None):
        print 'Initiating API'
        self.auth = auth_handler
        self.host = host
        self.api_root = api_root
        self.parser = parser # or ModelParser()

    # API methods 
    """
    Required arguments:
        'path' - The API method's URL path. 

    The optional arguments available are:
        'req_method'    - The HTTP request method to use: "GET", "POST", 
                          "DELETE", "PUT" ... Defaults to "GET" if argument 
                          is not provided.
        'payload_type'  - The name of the Model class that will retain and 
                          parse the response data.
        'payload_list'  - If True, a list of 'payload_type' objects is returned.
        'allowed_param' - A list of params that the API method accepts.
        'require_auth'  - True if the API method requires authentication.
    """
    
    get_sites = bind_method(
        path = 'getsites',
        payload_type = 'site',
        payload_list = True,
        allowed_param = [],
        require_auth = True
    )

    get_posts = bind_method(
        path = 'getsites',
        payload_type = 'Post',
        payload_list = True,
        allowed_param = ['site_id', 'hostname', 'num_posts', 'page', 'tag'],
        require_auth = True
    )

    new_post = bind_method(
        path = 'newpost',
        req_method = 'POST',
        payload_type = 'post',
        allowed_param = ['site_id', 'title', 'body', 'autopost', 'private',
                         'date', 'tags', 'source', 'sourceLink'],
        require_auth = True
    ) 

