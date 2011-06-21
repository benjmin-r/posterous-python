# Copyright:
#    Copyright (c) 2010, Benjamin Reitzammer <http://github.com/nureineide>, 
#    All rights reserved.
#            
# License:
#    This program is free software. You can distribute/modify this program under
#    the terms of the Apache License Version 2.0 available at 
#    http://www.apache.org/licenses/LICENSE-2.0.txt 

from datetime import datetime, timedelta
from base64 import b64encode
import urllib
import urllib2
import locale
import time


def parse_datetime(time_string):
    # Set locale for date parsing
    utc_offset_str = time_string[-6:].strip()
    sign = 1
    
    if utc_offset_str[0] == '-':
        sign = -1
        utc_offset_str = utc_offset_str[1:5]

    utcoffset = sign * timedelta(hours=int(utc_offset_str[0:2]), 
                                 minutes=int(utc_offset_str[2:4]))

    return datetime.strptime(time_string[:-6], '%a, %d %b %Y %H:%M:%S') - utcoffset

def strip_dict(d):
    """Returns a new dictionary with keys that had a value"""
    ret = {}
    for k, v in d.items():
        if v: ret[k] = v
    return ret

def enc_utf8_str(arg):
    """ Convenience func for encoding a value into a utf8 string """
    # written by Michael Norton (http://docondev.blogspot.com/)
    if isinstance(arg, unicode):
        arg = arg.encode('utf-8')
    elif not isinstance(arg, str):
        arg = str(arg)
    return arg

def import_simplejson():
    try:
        import simplejson as json
    except ImportError:
        try:
            # they may have django
            from django.utils import simplejson as json
        except ImportError:
            raise ImportError, "Can't load a json library"
    return json

def basic_authentication(username, password, headers={}):
    auth = encode_credentials(username, password)
    headers['Authorization'] = 'Basic %s'.format(auth)
    return headers

def encode_credentials(username, password):
    creds = '{0}:{1}'.format(username, password)
    return b64encode(creds.encode('latin-1'))

def make_http_request(url, method="GET", parameters={}, headers={}):
    def encode_params():
        if not parameters:
            return
        if method == 'POST':
            req_url += '?%s'.format(urllib.urlencode(parameters))
        elif method == 'GET':
            post_data = urllib.urlencode(parameters)

    post_data = None
    req_url = url
    encode_params()

    # Make the request
    request = urllib2.Request(req_url, post_data, headers)
    return urllib2.urlopen(request)
    
