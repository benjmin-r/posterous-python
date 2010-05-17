# Copyright:
#    Copyright (c) 2010, Benjamin Reitzammer <http://github.com/nureineide>, 
#    All rights reserved.
#            
# License:
#    This program is free software. You can distribute/modify this program under
#    the terms of the Apache License Version 2.0 available at 
#    http://www.apache.org/licenses/LICENSE-2.0.txt 

import logging


def bind_method(**options):

    class APIMethod(object):
        # Get the options for the api method
        path = options['path']
        payload_type = options.get('payload_type', None)
        payload_list = options.get('payload_list', False)
        allowed_param = options.get('allowed_param', [])
        req_method = options.get('req_method', 'GET')
        require_auth = options.get('require_auth', False)

        def __init__(self, api, args, kwargs):
            print 'Initialized APIMethod: args=%s, kw=%s' % (args, kwargs)
            
            # If the method requires authentication and no credentials
            # are provided, throw an error
            if self.require_auth and not api.auth:
                raise Exception('Authentication is required!')

            self.api = api


        def execute(self):
            print 'Executing api method'

    def _call(api, *args, **kwargs):
        logging.info('Calling API method')
        method = APIMethod(api, args, kwargs)
        return method.execute()

    return _call

