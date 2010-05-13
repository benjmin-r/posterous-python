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
import os.path
from datetime import datetime, timedelta
import urllib2, urllib
import helpers

class Posterous(object):
    """ """
    
    api_url = "https://posterous.com/api/"

    action_path = {
        'sites': 'getsites',
        'readposts': 'readposts',
        'post': 'newpost',
    }
    
    def __init__(self, username, password):
        logging.info("Initializing Posterous API with username '%s'" % username)
        self.username = username
        self.password = password
        
    def _build_url(self, url, data):
        return '%s?%s' % (url, data)

    def _encode_params(self, params):
        ret = []
        # remove empty fields from the dict
        params = helpers.strip_dict(params)

        for k, v in params.items():
            k = helpers.enc_utf8(k)
            if isinstance(v, list):
                # a list of values need to be turned into tuples
                # with the first index being the field name and the 
                # second being the value.
                ### NOTE if the value is file data, the utf8 encoding fails
                ### ... not sure what to do with this, so I'm removing the
                ### encoding for now.
                ret.extend(map(lambda tup: (k, tup), v))
            else:
                ret.append((k, helpers.enc_utf8(v)))
        return urllib.urlencode(ret)

    def _req(self, action, params):
        url = self.api_url + action
        data = self._encode_params(params)
        auth = b64encode("%s:%s" % (self.username, self.password))
        return (url, data, auth)

    def _get(self, action, params={}):
        """ GET request """
        url, data, auth = self._req(action, params) 
        logging.debug("Making a GET request to URL '%s'" % url)
        req = urllib2.Request(self._build_url(url, data), None, 
                              { "Authorization" : "Basic %s" % auth })
        return urllib2.urlopen(req).read()
        
    def _post(self, action, params={}):
        """ POST request """
        url, data, auth = self._req(action, params) 
        logging.debug("Making a POST request to URL '%s'" % url)
        req = urllib2.Request(url, data, 
                              { "Authorization" : "Basic %s" % auth })    
        return urllib2.urlopen(req).read()
    
    def get_posts(self, *args, **kw):
        """ 
        Invokes the 'readposts' method of the Posterous API.
        
        Simply pipes through arguments to the Posterous API. This means,
        that the names of the arguments passed to this method must 
        correspond with the variable names accepted by the Posterous API
        for the 'readposts' call.
        
        Currently these are the following:
            "site_id" - Optional. Id of the site to read from
            "hostname" - Optional. Subdomain of the site to read from
            "num_posts" - Optional. How many posts you want. Default is
                          10, max is 50
            "page" - Optional. What 'page' you want (based on 
                     num_posts). Default is 1
            "tag" - Optional
        
        No validation is done on the arguments. This means, the method 
        doesn't care if an invalid value like a negative num_posts is 
        provided. It's the responsibility of the caller to provide 
        correct values
        
        See http://posterous.com/api/reading for more details
        
        Returns a list of Post objects, may be an empty list 
        """
        logging.info("Trying to get posts with params: '%s'" % str(kw))
        return parse_posts_xml(self._get(self.action_path['readposts'], kw))
            
    def get_sites(self):
        """ 
        Invokes the 'getsites' method of the Posterous API.        
        See http://posterous.com/api/reading for more details
        
        Returns a list of Site objects, may be an empty list
        """
        logging.info("Trying to get all sites information")
        return parse_sites_xml(self._get(self.action_path['sites']))

    def new_post(self, **kw):
        """
        Returns a Posting object. Call the object's save() method to 
        send it to Posterous.
        """
        logging.info("Creating new post object")
        post = Posting(self, **kw)
        return post 


class Posting(object):
    """
    A class for creating a new post on a blog. The args are set by
    passing **kw args to the Posterous class or by setting them 
    directly. 

    To add media to the posting, call add_media().

    When the object is ready to be posted, call the save() method to 
    initiate the API request.
    """
    args = {
        'site_id': '',
        'media[]': '',
        'title': '',
        'body': '',
        'autopost': '',
        'private': '',
        'date': '',
        'source': '',
        'sourceLink': '',
    }

    ### TODO Need a type converter to change bools in the args to numbers
    ### TODO Need to parse the response like the get methods do

    def __init__(self, api_callback, **kw):
        # set the arg values if any were passed in
        for k, v in kw.iteritems():
            if k in self.args:
                self.args[k] = v
        
        self.__api_callback = api_callback
        self.media_data = []
        self.__dict__.update(self.args)

    def add_media(self, quiet=False, **kw):
        """
        Adds file data to the post. This method doesn't overwrite
        any previously added media. The supported method parameters 
        are:

        url - The URL of the file. Can be a list of url strings.
        path - The local path to the file. Can be a list of path strings.
        file - The contents of a read file. Can be a list.
        quiet - If False, an exception is immediately raised if a file
                cannot be found or opened. If True, the file is skipped.
        """
        ### TODO pull data from urls
       
        def from_path(path):
            # check if path exists and grab the file data
            if os.path.exists(path):
                file = open(path, 'rb')
                self.media_data.append(file.read())
                logging.info("Added file '%s' to media" % path.split('/')[-1])
                file.close()
            elif not quiet:
                raise Exception("Cannot add file to media as path '%s' does " \
                                "not exist." % path)

        # Check for file paths
        if 'path' in kw:
            path = kw['path']
            if isinstance(path, list):
                map(from_path, path)
            else:
                from_path(path)

        # Save the file data
        if 'file' in kw:
            file = kw['file']
            if isinstance(file, list):
                self.media_data += file
            else:
                self.media_data.append(file)
            logging.info("Added file data to media")

    def save(self):
        """ Saves the post to Posterous """
        logging.info("Saving post to posterous")

        if self.media_data:
            self.args['media[]'] = self.media_data
        
        resp = self.__api_callback._post('newpost', self.args)
        print '\nresp:\n%s' % resp

###
### Everything related to parsing responses
###

DATE_FORMAT = '%a, %d %b %Y %H:%M:%S'

def parse_date(value):
    try:
        # parse timezone manually & then calculate local time manually 
        offset = int(value[-5:])
        t = datetime.strptime(value[:-6], DATE_FORMAT)
        return t - timedelta(hours = offset / 100)
    except:
        logging.error("Error while manually parsing TZ info in date '%s'" % value)
        return None
        
        
def type_converter(tagname, value):
    def parse_bool(s):
        return True if s.lower() == 'true' else False
    
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
        'date': parse_date
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
        if name == 'err' and tagstack[-1] == 'rsp': 
            raise ApiError(attrs['msg'], attrs['status'])
        elif name == 'post': 
            resp.append(Post())
        elif name == 'comment': 
            resp.append(Comment())
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
            ## we can only find out if we're inside <media> of type image, 
            ## when we finished parsing <type>
            resp.append(Image())
            
        elif tagname == 'type' and elemtext == 'video':
            ## we can only find out if we're inside <media> of type video, 
            ## when we finished parsing <type>
            resp.append(Video())
            
        elif tagname == 'type' and elemtext == 'audio':
            ## we can only find out if we're inside <media> of type audio, 
            ## when we finished parsing <type>
            resp.append(Audio())
        
        elif o.whoami() == 'Comment' and tagname in Comment.args:
            ## parsing a child tag of <comment>
            o[tagname] = type_converter(tagname, elemtext)
            
        elif o.whoami() == 'Comment' and tagname == 'comment':
            ## a </comment> tag; remove Comment instance from stack and add 
            ## to latest Post instance
            comment = resp.pop()
            resp[-1].comments.append(comment)
            
        elif o.whoami() == 'Audio' and tagname in Audio.args:
            ## parsing a child tag of <media><type>audio</type>
            o[tagname] = type_converter(tagname, elemtext)
            
        elif o.whoami() == 'Video' and tagname in Video.args:
            ## parsing a child tag of <media><type>video</type>
            o[tagname] = type_converter(tagname, elemtext)
            
        elif o.whoami() == 'Image':
            ## tag before an actual image data, must be either <medium> or 
            ## <thumb>
            ## ... use it as prefix for Image instance attribute name
            sizetag = tagstack[-2]  
            img_attr_name = "%s_%s" % (sizetag, tagname)
            if sizetag in ('medium', 'thumb') and img_attr_name in Image.args:
                o[img_attr_name] = type_converter(img_attr_name, elemtext)
                
        if tagname == 'media':
            ## a </media> tag; remove Image/Audio/Video instance from stack 
            ## and add to latest Post instance
            img = resp.pop()
            resp[-1].media.append(img)
            
        ### FIXME formulate more compact withouth many if and elif using 
        ### some kind of mapping table
        
        tagstack.pop()
        

    parser = xml.parsers.expat.ParserCreate()
    parser.StartElementHandler = start_element
    parser.EndElementHandler = end_element
    parser.CharacterDataHandler = char_data
    parser.Parse(xml_string)
    return resp
        

class PosterousData(dict):
    """ 
    (private) Base class that provides nice utility methods for data 
    holding classes.
    """
    def __init__(self, **kw): 
        for k, v in self.args.iteritems(): 
            self[k] = v
        super(PosterousData, self).__init__(kw)
        self.__dict__ = self
        
    def __str__(self):
        state = ["%s=%r" % (a, v) for (a, v) in self.items()]
        return '{ %s\n}' % "\n  ".join(state).encode("utf-8") 

    def whoami(self):
        return type(self).__name__

        
class Site(PosterousData):
    """Data holder class for a posterous site"""
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
    """Data holder class for Posts"""
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
    """Data holder class for Media of type 'image'"""
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
    """Data holder class for Media of type 'audio'"""
    args = {
        'url': '', 
        'filesize': '', 
        'album': '', 
        'song': '', 
        'artist': '', 
    }


class Video(PosterousData):
    """Data holder class for Media of type 'video'"""
    args = {
        'url': '', 
        'filesize': '', 
        'thumb': '', 
        'flv': '', 
        'mp4': '', 
    }

         
class Comment(PosterousData):
    """Data holder class for a single Comment"""
    args = {
        'body': '', 
        'date': '', 
        'author': '', 
        'authorpic': '', 
    }


class ApiError:
    """Formats an error response"""
    msg = ''
    status_code = 0
    def __init__(self, msg, code):
        (self.msg, self.status_code) = (msg, code)
    
    def __str__(self):
        return "Posterous API Error: Code=%s, Message=%s" % (self.status_code, self.msg)
