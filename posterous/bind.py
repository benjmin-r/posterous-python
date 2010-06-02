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
from datetime import datetime
from base64 import b64encode

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
            if self.require_auth and not (api.username and api.password):
                raise Exception('Authentication is required!')

            self.api = api
            self.headers = kwargs.pop('headers', {})
            self.api_url = api.host + api.api_root
            self._build_parameters(args, kwargs)

        def _build_parameters(self, args, kwargs):
            self.parameters = []
            
            args = list(args)
            args.reverse()

            for name, p_type in self.allowed_param:
                value = None
                if args:
                    value = args.pop()

                if name in kwargs:
                    if not value:
                        value = kwargs.pop(name)
                    else:
                        raise TypeError('Multiple values for parameter %s '\
                                        'supplied!' % name)
                if not value:
                    continue

                if not isinstance(p_type, tuple):
                    p_type = (p_type,)

                self._check_type(value, p_type, name)
                self._set_param(name, value)
            
        def _check_type(self, value, p_type, name):
            """
            Throws a TypeError exception if the value type is not in the p_type
            tuple.
            """
            if not isinstance(value, p_type):
                raise TypeError('The value passed for parameter %s is not ' \
                                'valid! It must be one of these: %s' 
                                % (name, p_type))

            if isinstance(value, list):
                for val in value:
                    if isinstance(val, list) or not isinstance(val, p_type):
                        raise TypeError('A value passed for parameter %s is ' \
                                        'not valid. It must be one of these: ' \
                                        '%s' % (name, p_type))
            
        def _set_param(self, name, value):
            """Do appropriate type casts and utf-8 encode the parameter values"""
            if isinstance(value, bool):
                value = int(value)
            elif isinstance(value, datetime):
                value = '%s +0000' % value.strftime('%a, %d %b %Y %H:%M:%S').split('.')[0]
            elif isinstance(value, list):
                for val in value:
                    self.parameters.append(('%s[]' % name, enc_utf8_str(val)))
                return
            
            self.parameters.append((name, enc_utf8_str(value)))


        def execute(self):
            # Build request URL
            url = self.api_url + '/' + self.path

            # Apply authentication if required
            if self.api.username and self.api.password:
                auth = b64encode('%s:%s' % (self.api.username, self.api.password))
                self.headers['Authorization'] = 'Basic %s' % auth
           
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

