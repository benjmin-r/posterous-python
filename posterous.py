"""
Simple wrapper-lib for accessing the Posterous API via python.
See http://posterous.com/api

Copyright:
    Copyright (c) 2010, Benjamin Reitzammer <http://github.com/nureineide>, All rights reserved.
    
License:
    This program is free software. You can distribute/modify this program under 
    the terms of the Apache License Version 2.0 available at
    http://www.apache.org/licenses/LICENSE-2.0.txt 
"""

__author__ = "Benjamin Reitzammer <http://github.com/nureineide>"
__version__ = "0.1"

from base64 import b64encode
from copy import copy
import xml.parsers.expat
import logging 
from datetime import datetime
import urllib2, urllib


class Posterous(object):
    """ """
    
    urls = {
        'sites': 'https://posterous.com/api/getsites',
        'readposts': 'https://posterous.com/api/readposts',
    }
    
    def __init__(self, username, password):
        logging.info("Initializing Posterous API with username '%s'" % username)
        self.username = username
        self.password = password
        
    def _enc_utf8(self, s):
        """ Convenience func for encoding a string in utf8 """
        return s.encode('utf8')  

    def _build_url(self, url, data):
        return '%s?%s' % (url, urllib.urlencode( [ (self._enc_utf8(k), self._enc_utf8(v)) for (k, v) in data.items() ] ))

    def _get(self, url, params={}):
        logging.debug("Trying to get contents of URL '%s'" % url)
        req = urllib2.Request(self._build_url(url, params), None, 
                { "Authorization" : "Basic %s" % b64encode("%s:%s" % (self.username, self.password)) }
            )
        return urllib2.urlopen(req).read()
            
    def get_posts(self, site_id):
        """ returns a list of Post objects, may be an empty list """
        logging.info("Trying to get posts for Site ID '%s'" % site_id)
        return parse_posts_xml( self._get(self.urls['readposts'], {'site_id': str(site_id)}) )
    
    def get_sites(self):
        """ returns a list of Site objects, may be an empty list """
        logging.info("Trying to get all sites information")
        return parse_sites_xml( self._get(self.urls['sites']) )
        

###
### Everything related to parsing responses
###

DATE_FORMAT = '%a, %d %b %Y %H:%M:%S -0800'

def type_converter(tagname, value):
    def parse_bool(s):
        if s.lower() == 'true':return True
        else: return False
        
    converter_map = {
            'id': int,
            'views': int,
            'num_posts': int,
            'filesize': int,
            'thumb_filesize': int,
            'medium_filesize': int,
            'thumb_width': int,
            'medium_width': int,
            'thumb_height': int,
            'medium_height': int,
            'private': parse_bool,
            'primary': parse_bool,
            'commentsenabled': parse_bool,
            'date': lambda v: datetime.strptime(v, DATE_FORMAT)
        }
    return converter_map[tagname](value) if tagname in converter_map else value


def parse_sites_xml(xml_string):
    """ returns a list of Site() objects """
    resp = []
    tagstack = []
    str_list = []
        
    def start_element(name, attrs):
        if name == 'err' and tagstack[-1] == 'rsp':
            raise ApiError(attrs['msg'], attrs['status'])
        elif name == 'site':
            resp.append( Site() )
        tagstack.append(name)
        del str_list[:]
        
    def char_data(chardata):
        tagname = tagstack[-1]
        str_list.append(chardata)
        
    def end_element(name):
        if name in Site.args: 
            resp[-1][name] = type_converter(name, ''.join(str_list))
        tagstack.pop()
        
    parser = xml.parsers.expat.ParserCreate()
    parser.StartElementHandler = start_element
    parser.EndElementHandler = end_element
    parser.CharacterDataHandler = char_data
    parser.Parse(xml_string)
    return resp


def parse_posts_xml(xml_string):
    """ returns a list of Post() objects """
    resp = []
    tagstack = []
    str_list = []
    
    def start_element(name, attrs):
        if name == 'err' and tagstack[-1] == 'rsp': raise ApiError(attrs['msg'], attrs['status'])
        elif name == 'post': resp.append( Post() )
        elif name == 'comment': resp.append( Comment() )
        tagstack.append(name)
        del str_list[:]
        
    def char_data(chardata):
        tagname = tagstack[-1]
        str_list.append(chardata)
        
    def end_element(tagname):
        o = resp[-1]
        elemtext = ''.join(str_list) # ugly hack to avoid UnboundLocalError
        
        if o.whoami() == 'Post' and tagname in Post.args:
            ## most common case: We're parsing a child tag of <post>
            o[tagname] = type_converter(tagname, elemtext)
            
        elif tagname == 'type' and elemtext == 'image':
            ## we can only find out if we're inside <media> of type image, when we finished parsing <type>
            resp.append(Image())
            
        elif tagname == 'type' and elemtext == 'video':
            ## we can only find out if we're inside <media> of type video, when we finished parsing <type>
            resp.append(Video())
            
        elif tagname == 'type' and elemtext == 'audio':
            ## we can only find out if we're inside <media> of type audio, when we finished parsing <type>
            resp.append(Audio())
        
        elif o.whoami() == 'Comment' and tagname in Comment.args:
            ## parsing a child tag of <comment>
            o[tagname] = type_converter(tagname, elemtext)
            
        elif o.whoami() == 'Comment' and tagname == 'comment':
            ## a </comment> tag; remove Comment instance from stack and add to latest Post instance
            comment = resp.pop()
            resp[-1].comments.append(comment)
            
        elif o.whoami() == 'Audio' and tagname in Audio.args:
            ## parsing a child tag of <media><type>audio</type>
            o[tagname] = type_converter(tagname, elemtext)
            
        elif o.whoami() == 'Video' and tagname in Video.args:
            ## parsing a child tag of <media><type>video</type>
            o[tagname] = type_converter(tagname, elemtext)
            
        elif o.whoami() == 'Image':
            # tag before an actual image data, must be either <medium> or <thumb>
            # ... use it as prefix for Image instance attribute name
            sizetag = tagstack[-2]  
            img_attr_name = "%s_%s" % (sizetag, tagname)
            if sizetag in ('medium', 'thumb') and img_attr_name in Image.args:
                o[img_attr_name] = type_converter(img_attr_name, elemtext)
                
        if tagname == 'media':
            ## a </media> tag; remove Image/Audio/Video instance from stack and add to latest Post instance
            img = resp.pop()
            resp[-1].media.append(img)
            
        ### FIXME formulate more compact withouth many if and elif using some kind of mapping table
        
        tagstack.pop()
        
        
    parser = xml.parsers.expat.ParserCreate()
    parser.StartElementHandler = start_element
    parser.EndElementHandler = end_element
    parser.CharacterDataHandler = char_data
    parser.Parse(xml_string)
    return resp
    
        
class PosterousData(dict):
    """ (private) Base class that provides nice utility methods for data holding classes
    """
    def __init__(self, **kw):                 
        for k, v in self.args.iteritems(): self[k] = v  
        super(PosterousData, self).__init__(kw)
        self.__dict__ = self
        
    def __str__(self):
        state = ["%s=%r" % (a, v) for (a, v) in self.items()]
        return '{ %s\n}' % "\n  ".join(state).encode("utf-8") 

    def whoami(self):
        return type(self).__name__


class Site(PosterousData):
    """Data holder class for a posterous site
    """
    args = {
        'id': '', 
        'name': '', 
        'url': '', 
        'private': '', 
        'hostname': '', 
        'primary': '', 
        'commentsenabled': '', 
        'num_posts': '', 
    }

        
class Post(PosterousData):
    """Data holder class for Posts 
    """
    args = {
        'title': '', 
        'url': '', 
        'link': '', 
        'id': '',
        'body': '', 
        'date': '', 
        'views': '',
        'private': '',
        'author': '', 
        'authorpic': '', 
        'commentsenabled': '',
    }
            
    def __init__(self, **kw):                 
        PosterousData.__init__(self, **kw)
        self['comments'] = [] 
        self['media'] = [] 


class Image(PosterousData):
    """Data holder class for Media of type 'image'
    """
    args = {
        'medium_filesize': '', 
        'medium_height': '', 
        'medium_width': '', 
        'medium_url': '', 
        'thumb_filesize': '', 
        'thumb_height': '', 
        'thumb_width': '', 
        'thumb_url': '', 
    }


class Audio(PosterousData):
    """Data holder class for Media of type 'audio'
    """
    args = {
        'url': '', 
        'filesize': '', 
        'album': '', 
        'song': '', 
        'artist': '', 
    }


class Video(PosterousData):
    """Data holder class for Media of type 'video'
    """
    args = {
        'url': '', 
        'filesize': '', 
        'thumb': '', 
        'flv': '', 
        'mp4': '', 
    }

         
class Comment(PosterousData):
    """Data holder class for a single Comment
    """
    args = {
        'body': '', 
        'date': '', 
        'author': '', 
        'authorpic': '', 
    }


class ApiError:
    """ """
    msg = ''
    status_code = 0
    def __init__(self, msg, code):
        (self.msg, self.status_code) = (msg, code)
    
    def __str__(self):
        return "Posterour API Error: Code=%s, Message=%s" % (self.status_code, self.msg)
