def strip_dict(d):
    """Returns a new dictionary with keys that had a value"""
    ret = {}
    for k, v in d.items():
        if v: ret[k] = v
    return ret

def enc_utf8(s):
    """ Convenience func for encoding a string in utf8 """
    return str(s).encode('utf8')

