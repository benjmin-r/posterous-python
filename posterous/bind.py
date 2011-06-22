# Copyright:
#    Copyright (c) 2010, Benjamin Reitzammer <http://github.com/nureineide>, 
#    All rights reserved.
#            
# License:
#    This program is free software. You can distribute/modify this program under
#    the terms of the Apache License Version 2.0 available at 
#    http://www.apache.org/licenses/LICENSE-2.0.txt 

from datetime import datetime
from os.path import join
from posterous.utils import enc_utf8_str, make_http_request, basic_authentication


def bind_method(**options):        
    def _call(api, *args, **kwargs):
        method = APIMethod(api, options, args, kwargs)
        return method.execute()
    return _call

class APIMethod(object):
    def __init__(self, api, method_options, args, kwargs):
        self.api = api
        self.headers = kwargs.pop('headers', {})

        # Get the options for the api method
        self.path = method_options['path']
        self.payload_type = method_options.get('payload_type', None)
        self.allowed_params = method_options.get('parameters', [])
        self.method = method_options.get('method', 'GET')
        self.require_auth = method_options.get('require_auth', None)

        self._build_parameters(args, kwargs)

    def execute(self):
        # Apply authentication if required
        self._check_authentication()

        try:
            # Make the web request
            url = join(self.api.api_url, self.path)
            resp = make_http_request(url, self.method, self.parameters, self.headers)
        except Exception, e:
            raise Exception("Failed to send request: {0}".format(e))

        # Return the parsed payload. Will be a model instance if the default 
        # parser is used
        return self.api.parser.parse(self, resp.read())

    def _check_authentication(self):
        if not self.require_auth:
            return
        
        # Apply basic authentication
        if not (self.api.username and self.api.password):
            raise Exception("This call requires a username and password for " \
                            "authentication!")
        else:
            basic_authentication(self.api.username, self.api.password, self.headers)

        # Apply the API token for additional authentication
        token = self.api.token
        if not token:
            raise Exception("This call requires an API token for authentication!")
        else:
            self._set_authentication_token(token)

    def _set_authentication_token(self, token):
        self.parameters.append(('api_token', enc_utf8_str(token)))

    def _build_parameters(self, args, kwargs):
        self.parameters = []
        args = list(args)
        args.reverse()

        for name, p_type in self.allowed_params:
            value = None

            if args:
                value = args.pop()
            if name in kwargs:
                if not value:
                    value = kwargs.pop(name)
                else:
                    raise TypeError("Multiple values for parameter {0} " \
                                    "supplied!".format(name))
            
            if not value:
                continue

            if not isinstance(p_type, tuple):
                p_type = (p_type,)

            self._check_type(value, p_type, name)
            self._set_param(name, value)
        
    def _check_type(self, value, p_type, name):
        """
        Throws a TypeError exception if the value type is not in the p_type tuple.
        """
        if not isinstance(value, p_type):
            raise TypeError("The value passed for parameter {0} is not valid! " \
                            "It must be one of these: {1}".format(name, p_type))

        if isinstance(value, list):
            for val in value:
                if isinstance(val, list) or not isinstance(val, p_type):
                    raise TypeError("A value passed for parameter {0} is not valid. " \
                                    "It must be one of these: {1}".format(name, p_type))
        
    def _set_param(self, name, value):
        """Do appropriate type casts and utf-8 encode the parameter values"""
        val = None

        if isinstance(value, bool):
            val = int(value)
        elif isinstance(value, datetime):
            timestamp = value.strftime('%a, %d %b %Y %H:%M:%S').split('.')[0]
            val = '{0} +0000'.format(timestamp)
        elif isinstance(value, list):
            for v in value:
                self.parameters.append(('{0}[]'.format(name), enc_utf8_str(v)))
            return

        self.parameters.append((name, enc_utf8_str(val)))

    
