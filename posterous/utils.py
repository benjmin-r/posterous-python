# Copyright:
#    Copyright (c) 2010, Benjamin Reitzammer <http://github.com/nureineide>, 
#    All rights reserved.
#            
# License:
#    This program is free software. You can distribute/modify this program under
#    the terms of the Apache License Version 2.0 available at 
#    http://www.apache.org/licenses/LICENSE-2.0.txt 

from datetime import datetime
import locale
import time


def parse_datetime(string):
    # Set locale for date parsing
    locale.setlocale(locale.LC_TIME, 'C')
    # Must parse datetime this way to work in python 2.4
    date = datetime(*(time.strptime(string, '%a %b %d %H:%M:%S +0000 %Y')[0:6]))

    # Reset the locale back to default setting
    locale.setlocale(locale.LC_TIME, '')
    return date

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
