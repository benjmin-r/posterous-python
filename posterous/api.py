# Copyright:
#    Copyright (c) 2010, Benjamin Reitzammer <http://github.com/nureineide>, 
#    All rights reserved.
#            
# License:
#    This program is free software. You can distribute/modify this program under
#    the terms of the Apache License Version 2.0 available at 
#    http://www.apache.org/licenses/LICENSE-2.0.txt 

from posterous.bind import bind_method
from posterous.utils import *


class API(object):
    def __init__(self, auth_handler=None, host='posterous.com',
                 api_root='/api', parser=None):
        self.auth = auth_handler
        self.host = host
        self.api_root = api_root
        self.parser = parser # or ModelParser()

    ## API methods 
    """
    Required arguments:
        'path' - The API method's URL path. 

    The optional arguments available are:
        'method'        - The HTTP request method to use: "GET", "POST", 
                          "DELETE" ... Defaults to "GET" if argument 
                          is not provided.
        'payload_type'  - The name of the Model class that will retain and 
                          parse the response data.
        'payload_list'  - If True, a list of 'payload_type' objects is returned.
        'allowed_param' - A list of params that the API method accepts.
        'require_auth'  - True if the API method requires authentication.
    """
    
    ## Reading 
    """
    Returns a list of all sites owned and authored by the 
    authenticated user.
    """
    get_sites = bind_method(
        path = 'getsites',
        payload_type = 'site',
        payload_list = True,
        allowed_param = [],
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
        allowed_param = ['site_id', 'hostname', 'num_posts', 'page', 'tag'],
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
        allowed_param = ['id'],
        require_auth = False
    )
        
    """
    Returns a list of tags for a post. Authentication is 
    optional. If it's not authenticated, either the site_id or 
    hostname is required and only tags in public posts/sites 
    will be returned.
    """
    get_tags = bind_method(
        path = 'gettags',
        payload_type = 'tag',
        payload_list = True,
        allowed_param = ['site_id', 'hostname'],
        require_auth = False
    )

    ## Posting
    """
    Returns a new post.
    The media param must be set to file data. If posting 
    multiple files, provide a list of file data.
    """
    new_post = bind_method(
        path = 'newpost',
        method = 'POST',
        payload_type = 'post',
        allowed_param = ['site_id', 'title', 'body', 'media', 'autopost', 
                         'private', 'date', 'tags', 'source', 'sourceLink'],
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
        allowed_param = ['post_id', 'title', 'body', 'media'],
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
        allowed_param = ['post_id', 'comment', 'name', 'email', 'date'],
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
        allowed_params = ['username', 'password', 'media', 'message', 'body', 
                          'source', 'sourceLink']
    )
        
    """
    Has the same functionality of 'twitter_upload', while
    also tweeting the message with a link.
    """
    twitter_upload_and_post = bind_method(
        path = 'uploadAndPost',
        method = 'POST',
        payload_type = 'json',
        allowed_params = ['username', 'password', 'media', 'message', 'body', 
                          'source', 'sourceLink']
    )
        
