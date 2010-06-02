# Copyright:
#    Copyright (c) 2010, Benjamin Reitzammer <http://github.com/nureineide>, 
#    All rights reserved.
#            
# License:
#    This program is free software. You can distribute/modify this program under
#    the terms of the Apache License Version 2.0 available at 
#    http://www.apache.org/licenses/LICENSE-2.0.txt 

from posterous.utils import parse_datetime


class ResultSet(list):
    """ A list like object that holds results from a Posterous API query. """


class Model(object):
    """ Base class """
    def __init__(self, api=None):
        self._api = api


class Post(Model):
    @classmethod
    def parse(self, api, json):
        post = self(api)
        for k, v in json.items():
            if k == 'media':
                setattr(post, k, Media.parse(api, v))
            elif k == 'comment':
                setattr(post, k, Comment.parse(api, v))
            else: 
                setattr(post, k, v)
        return post

    @classmethod
    def parse_list(self, api, json_list):
        results = ResultSet()
        for obj in json_list:
            results.append(self.parse(api, obj))
        return results

    def update(self, *args, **kwargs):
        return self._api.update_post(self.id, *args, **kwargs)

    def new_comment(self, *args, **kwargs):
        return self._api.new_comment(self.id, *args, **kwargs)


class Site(Model):
    @classmethod
    def parse(self, api, json):
        site = self(api)
        for k, v in json.items():
            setattr(site, k, v)
        return site

    @classmethod
    def parse_list(self, api, json_list):
        results = ResultSet()
        for obj in json_list:
            results.append(self.parse(api, obj))
        return results

    def read_posts(self, **kwargs):
        return self._api.read_posts(self.id, **kwargs)

    def new_post(self, *args, **kwargs):
        return self._api.new_post(self.id, *args, **kwargs)

    def tags(self):
        return self._api.get_tags(self.id)


class Comment(Model):
    @classmethod
    def parse(self, api, json):
        comment = self(api)
        for k, v in json.items():
            if k == 'date':
                setattr(comment, k, parse_datetime(v))
            else:
                setattr(comment, k, v)
        return comment


class Tag(Model):
    @classmethod
    def parse(self, api, json):
        tag = self(api)
        for k, v in json.items():
            setattr(tag, k, v)
        return tag

    @classmethod
    def parse_list(self, api, json_list):
        results = ResultSet()
        for obj in json_list:
            results.append(self.parse(api, obj))
        return results

    def __str__(self):
        try:
            return self.tag_string
        except AttributeError:
            return ''
    

class Media(Model):
    @classmethod
    def parse(self, api, json, obj=None):
        media = obj or self(api)
        for k, v in json.items():
            if k == 'medium':
                Media.parse(api, v, media)
            elif k == 'thumb':
                setattr(media, k, Media.parse(api, v))
            else:
                setattr(media, k, v)
        return media

    def download(self):
        # download file
        pass


class JSONModel(Model):
    @classmethod
    def parse(self, api, json):
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

