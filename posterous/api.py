# Copyright:
#    Copyright (c) 2010, Benjamin Reitzammer <http://github.com/nureineide>, 
#    All rights reserved.
#            
# License:
#    This program is free software. You can distribute/modify this program under
#    the terms of the Apache License Version 2.0 available at 
#    http://www.apache.org/licenses/LICENSE-2.0.txt 

from datetime import datetime
from urlparse import urljoin

from posterous.parsers import ModelParser
from posterous.bind import bind_method


class API(object):
    """
    The API object defines a set of methods that interact with the Posterous API.
    The methods are defined with various arguments. These arguments are as follows:
        `path`: `(required)` The API method's endpoint URL
        `method`: `(optional)` HTTP request method. Use GET `(default)`, POST, or DELETE
        `payload_type`: The model to use when parsing
        `parameters`: List of parameters supplied to the call, as found on 
                      apidocs.posterous.com
                      Must be formatted as a list of tuples, with the param name being
                      paired with the expected value type. If more than one type is 
                      allowed, place the types in a tuple.
        `require_auth`: True if the call requires authentication. The default is False

    :param username: the Posterous user account to authenticate with 
    :param password: the password for the authenticating account
    :param api_token: a user account's API token. This is provided on the Posterous API site.
    :param parser: the parser for parsing the response payload
    """
    def __init__(self, username=None, password=None, api_token=None, parser=None):
        self.username = username
        self.password = password
        self.token = api_token
        self.host = 'https://posterous.com'
        self.api_root = '/api/2'
        self.api_url = self.host + self.api_root
        self.parser = parser or ModelParser()

    # Reading 
    # ----------------------------------------

    #: Returns a list of all sites owned and authored by the authenticated user.
    get_sites = bind_method(
        path = 'sites',
        payload_type = 'site',
        require_auth = True
    )

    """
    Returns a list of posts. Authentication is optional.
    If it's not authenticated, either the site_id or hostname
    is required and only public posts will be returned.
    """
    read_posts = bind_method(
        path = 'readposts',
        payload_type = 'post',
        payload_list = True,
        allowed_param = [
            ('site_id', int), 
            ('hostname', basestring), 
            ('num_posts', int), 
            ('page', int),
            ('tag', basestring)],
        require_auth = False
    )

    """
    Returns a post by interacting with the Post.ly API. 
    The id param must be in Post.ly shortcode. 
    (Example: 123abc in http://post.ly/123abc)
    Authentication is required if the post is private.
    """
    get_post = bind_method(
        path = 'getpost',
        payload_type = 'post',
        allowed_param = [('id', basestring)],
        require_auth = False
    )
        
    """
    Returns a list of all post tags. Authentication is 
    optional. If it's not authenticated, either the site_id or 
    hostname is required and only tags in public posts/sites 
    will be returned.
    """
    get_tags = bind_method(
        path = 'gettags',
        payload_type = 'tag',
        payload_list = True,
        allowed_param = [
            ('site_id', int),
            ('hostname', basestring)],
        require_auth = False
    )

    ## Posting
    """
    Creates a new post and returns a post object.
    The media param must be set to file data. If posting 
    multiple files, provide a list of file data.
    """
    new_post = bind_method(
        path = 'newpost',
        method = 'POST',
        payload_type = 'post',
        allowed_param = [
            ('site_id', int), 
            ('title', basestring),
            ('body', basestring), 
            ('media', (basestring, list)), 
            ('autopost', bool), 
            ('private', bool), 
            ('date', datetime), 
            ('tags', basestring), 
            ('source', basestring), 
            ('sourceLink', basestring)],
        require_auth = True
    )

    """
    Returns an updated post.
    The media param must be set to file data. If posting 
    multiple files, provide a list of file data.
    """
    update_post = bind_method(
        path = 'updatepost',
        method = 'POST',
        payload_type = 'post',
        allowed_param = [
            ('post_id', int),
            ('title', basestring),
            ('body', basestring), 
            ('media', (basestring, list))],
        require_auth = True
    )
   
    """
    Returns a comment with its accompanying post.
    If a name is not provided, the authenticated user will 
    own the comment. Optionally, a name and email may be 
    provided to create an anonymous comment; only the site
    owner can do this.
    """
    new_comment = bind_method(
        path = 'newcomment',
        method = 'POST',
        payload_type = 'comment',
        allowed_param = [
            ('post_id', int), 
            ('comment', basestring),
            ('name', basestring),
            ('email', basestring),
            ('date', datetime)],
        require_auth = True
    )

    ## Twitter
    """
    Allows the posting of media to Posterous using Twitter
    credentials. Username and password are required params.
    If the Twitter user is registered on Posterous, it will 
    post to their default site. If not registered, Posterous
    will create a new site for them.

    The media param must be set to file data. If posting
    multiple files, provide a list of file data.
        
    Returns a JSON object with the post id and post url.
    """
    twitter_upload = bind_method(
        path = 'upload',
        method = 'POST',
        payload_type = 'json',
        response_type = 'json',
        allowed_params = [
            ('username', basestring), 
            ('password', basestring), 
            ('media', (basestring, list)),
            ('message', basestring),
            ('body', basestring),
            ('source', basestring),
            ('sourceLink', basestring)]
    )
        
    """
    Has the same functionality of 'twitter_upload', while
    also tweeting the message with a link.
    """
    twitter_upload_and_post = bind_method(
        path = 'uploadAndPost',
        method = 'POST',
        payload_type = 'json',
        response_type = 'json',
        allowed_params = [
            ('username', basestring), 
            ('password', basestring), 
            ('media', (basestring, list)),
            ('message', basestring),
            ('body', basestring),
            ('source', basestring),
            ('sourceLink', basestring)]
    )
        
