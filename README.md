# What is posterous-python?
It's a simple to use Python library for the [Posterous API](http://posterous.com/api). 
It covers the entire API and it's really easy to extend when new API methods are added!

## Getting started
 * Check out the posterous-python source code using git:
        git clone git://github.com/nureineide/posterous-python.git
 * Run setuptools to install 
        sudo python setup.py install

That's it! Now fire up the posterous-shell to start playing with the library.

##Sample usage
    import posterous
     
    api = posterous.API('username', 'password')

    # Get the user's sites
    sites = api.get_sites()

    for site in sites:
        print site.name

    # Get all of the posts from the first site
    for post in api.read_posts(id=sites[0].id):
        print '%s (%s)' % (post.title, post.url)
        print '  - written by %s' % post.author

        if post.commentsenabled:
            print '  - has %s comment(s)' % post.commentscount
            
            if post.commentscount > 0:
                print '  - comments:'
                for comment in post.comments:
                    print '    - "%s" by %s' % (comment.body, comment.author)

        if hasattr(post, 'media'):
            print '  - media:'
            for media in post.media:
                print '    - %s' % media.url
 
        print '\n'


    # Create a new post with an image
    image = open("jellyfish.png", "rb").read()
    post = api.new_post(title="I love Posterous", body="Do you love it too?", media=image)

    # Add a comment
    post.new_comment("This is a really interesting post.")
   
Until there is full documentation coverage, you can take a look at api.py for the available methods and their arguments. The model objects also have methods that allow you to quickly perform actions (i.e. post.new_comment() instead of api.read_posts()[0].new_comment()), so look at models.py for those.

##In the future...
Expect to see these new features:

 * Easy pagination for iterating over large result sets
 * Response caching
 * Full documentation
 * A cool script for backing up a Posterous site

##Last words
The design of this library was very much inspired by [Tweepy](http://github.com/joshthecoder/tweepy). Tweepy is an excellent Python wrapper for Twitter's API, so give it a look if you're working with Twitter.

###License
[http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0) - See LICENSE for more details.

Copyright (c) 2010 Benjamin Reitzammer <[nureineide](http://github.com/nureineide)>

###Credits
Michael Campagnaro <[mikecampo](http://github.com/mikecampo)>
