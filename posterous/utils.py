# Copyright:
#    Copyright (c) 2010, Benjamin Reitzammer <http://github.com/nureineide>, 
#    All rights reserved.
#            
# License:
#    This program is free software. You can distribute/modify this program under
#    the terms of the Apache License Version 2.0 available at 
#    http://www.apache.org/licenses/LICENSE-2.0.txt 


def strip_dict(d):
    """Returns a new dictionary with keys that had a value"""
    ret = {}
    for k, v in d.items():
        if v: ret[k] = v
    return ret


def enc_utf8(s):
    """ Convenience func for encoding a string in utf8 """
    return str(s).encode('utf8')


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
