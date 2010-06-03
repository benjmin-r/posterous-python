# Copyright:
#    Copyright (c) 2010, Benjamin Reitzammer <http://github.com/nureineide>, 
#    All rights reserved.
#            
# License:
#    This program is free software. You can distribute/modify this program under
#    the terms of the Apache License Version 2.0 available at 
#    http://www.apache.org/licenses/LICENSE-2.0.txt 

from posterous.utils import parse_datetime


class Model(object):
    """ Base class """
    def __init__(self, api=None):
        self._api = api
 
    @classmethod
    def parse(self, api, json):
        if isinstance(json, list):
            return self.parse_list(api, json)
        else:
            return self.parse_obj(api, json)

    @classmethod
    def parse_list(self, api, json_list):
        results = list()
        for obj in json_list:
            results.append(self.parse_obj(api, obj))
        return results


class Post(Model):
    @classmethod
    def parse_obj(self, api, json):
        post = self(api)
        for k, v in json.iteritems():
            if k == 'media':
                setattr(post, k, Media.parse(api, v))
            elif k == 'comment':
                setattr(post, k, Comment.parse(api, v))
            else: 
                setattr(post, k, v)
        return post

    def update(self, *args, **kwargs):
        return self._api.update_post(self.id, *args, **kwargs)

    def new_comment(self, *args, **kwargs):
        return self._api.new_comment(self.id, *args, **kwargs)


class Site(Model):
    @classmethod
    def parse_obj(self, api, json):
        site = self(api)
        for k, v in json.iteritems():
            setattr(site, k, v)
        return site

    def read_posts(self, **kwargs):
        return self._api.read_posts(self.id, **kwargs)

    def new_post(self, *args, **kwargs):
        return self._api.new_post(self.id, *args, **kwargs)

    def tags(self):
        return self._api.get_tags(self.id)


class Comment(Model):
    @classmethod
    def parse_obj(self, api, json):
        comment = self(api)
        for k, v in json.iteritems():
            setattr(comment, k, v)
        return comment


class Tag(Model):
    @classmethod
    def parse_obj(self, api, json):
        tag = self(api)
        for k, v in json.iteritems():
            setattr(tag, k, v)
        return tag

    def __str__(self):
        try:
            return self.tag_string
        except AttributeError:
            return ''
    

class Media(Model):
    @classmethod
    def parse_obj(self, api, json, obj=None):
        # attributes from the medium tag are set on original Media object.
        media = obj or self(api)
        for k, v in json.iteritems():
            if k == 'medium':
                Media.parse_obj(api, v, media)
            elif k == 'thumb':
                setattr(media, k, Media.parse_obj(api, v))
            else:
                setattr(media, k, v)
        return media

    def download(self):
        # TODO: download file
        pass


class JSONModel(Model):
    @classmethod
    def parse_obj(self, api, json):
        return json


class ModelFactory(object):
    """
    Used by parsers for creating instances of models. 
    """
    post = Post
    site = Site
    comment = Comment
    tag = Tag
    media = Media
    json = JSONModel

"""Used to cast response tags to the correct type"""
attribute_map = {
    ('id', 'views', 'count', 'filesize', 'height', 'width', 'commentscount', 
     'num_posts'): int,
    ('private', 'commentsenabled', 'primary'): lambda v: v.lower() == 'true',
    ('date'): lambda v: parse_datetime(v)
}

