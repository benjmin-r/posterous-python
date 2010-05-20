# Copyright:
#    Copyright (c) 2010, Benjamin Reitzammer <http://github.com/nureineide>, 
#    All rights reserved.
#            
# License:
#    This program is free software. You can distribute/modify this program under
#    the terms of the Apache License Version 2.0 available at 
#    http://www.apache.org/licenses/LICENSE-2.0.txt 

import urllib
import urllib2
import logging

from posterous.utils import enc_utf8_str


def bind_method(**options):

    class APIMethod(object):
        # Get the options for the api method
        path = options['path']
        payload_type = options.get('payload_type', None)
        payload_list = options.get('payload_list', False)
        response_type = options.get('response_type', 'xml')
        allowed_param = options.get('allowed_param', [])
        method = options.get('method', 'GET')
        require_auth = options.get('require_auth', False)

        def __init__(self, api, args, kwargs):
            # If the method requires authentication and no credentials
            # are provided, throw an error
            if self.require_auth and not api.auth:
                raise Exception('Authentication is required!')

            self.api = api
            self.headers = kwargs.pop('headers', {})
            self.api_url = api.host + api.api_root
            self.build_parameters(args, kwargs)

        def build_parameters(self, args, kwargs):
            self.parameters = []
            
            for idx, arg in enumerate(args):
                try:
                    key = self.allowed_param[idx]
                except IndexError:
                    raise Exception('Too many parameters supplied!')
                
                if isinstance(arg, list):
                    key = key + '[]'
                    self.parameters.extend(map(lambda val: (key, 
                                           enc_utf8_str(val)), arg))
                else:
                    self.parameters.append((key, enc_utf8_str(arg)))

            for k, v in kwargs.items():
                if not v:
                    continue
                if k in self.parameters:
                    raise Exception('Multiple values for parameter %s '\
                                    'supplied!' % k)
                if isinstance(v, list):
                    k = k + '[]'
                    self.parameters.extend(map(lambda val: (k, 
                                           enc_utf8_str(val)), v))
                else:
                    self.parameters.append((k, enc_utf8_str(v)))

        def execute(self):
            # Build request URL
            url = self.api_url + '/' + self.path

            # Apply authentication if required
            if self.api.auth:
                self.api.auth.apply_auth(self.headers)
           
            # Encode the parameters
            post_data = None
            if self.method == 'POST':
                post_data = urllib.urlencode(self.parameters)
            elif self.method == 'GET' and self.parameters:
                url = '%s?%s' % (url, urllib.urlencode(self.parameters))
            
            # Make the request
            try:
                request = urllib2.Request(url, post_data, self.headers)
                resp = urllib2.urlopen(request)
            except Exception, e:
                # TODO: do better parsing of errors
                raise Exception('Failed to send request: %s' % e)

            return self.api.parser.parse(self, resp.read())

    
    def _call(api, *args, **kwargs):
        method = APIMethod(api, args, kwargs)
        return method.execute()

    return _call

