"""
    needs python 2.6
"""

from __future__ import with_statement
from optparse import OptionParser
import logging 
import datetime
import os, os.path
import re
import sys
import urlparse, urllib
import simplejson

from posterous.api import Posterous


class JsonDateEncoder(simplejson.JSONEncoder):
    def default(self, o):
        try:
            if o and type(o) == datetime.datetime:
                return str(o).encode('utf8')
        except TypeError:
            pass
        return simplejson.JSONEncoder.default(self, o)


if __name__ == '__main__':
    """
        Create a folder structure where 
        /{options.folder}
            /{site.hostname}
                site-{site.hostname}.json
                {post-slug}.json  <-- contains body & comments & everything else
                {post-slug}_media{num}
    """
    
    batch_sz = 50 # default (and current api max)
    opt_parser = OptionParser()
    
    opt_parser.add_option("-u", "--username", dest="username", 
        help="Email address associated with posterous account")
    
    opt_parser.add_option("-p", "--password", dest="password", 
        help="Password associated with posterous account")
    
    opt_parser.add_option("-f", "--folder", dest="folder", default="backup",
        help="Folder to store backup data in (Beware, if it exists, " \
             "data may be overwritten). Defaults to backup/")
    
    opt_parser.add_option("-s", "--site-id", type="int", dest="site_id",                
        help="Only query site with this id")
    
    opt_parser.add_option("-b", "--batch-size", type="int", dest="batch_size", 
        default=batch_sz, help="The number of posts to get per API call. " \
                               "Default is %d" % batch_sz)
    
    opt_parser.add_option("-d", "--debug", dest="debug", action="store_true", 
        default=False, help="Debug output")
    
    opt_parser.add_option("-v", "--verbose", dest="verbose", 
        action="store_true", default=False, help="Verbose output (overrides -d)")
    
    opt_parser.add_option("-q", "--quiet", dest="quiet", action="store_true", 
        default=True, help="Quiet output (overrides -v and -d)")
    
    # get the command line args
    (options, args) = opt_parser.parse_args()
    
    if options.debug:
        logging.basicConfig(level=logging.DEBUG)
    elif options.verbose:
        logging.basicConfig(level=logging.INFO)
    elif options.quiet:
        logging.basicConfig(level=logging.WARNING)
    
    if not options.username or not options.password:
        print "You must provide a username and password.\n"
        opt_parser.print_help()
        sys.exit()

    # Make the API calls and parse the data
    posterous = Posterous(options.username, options.password)

    for site in posterous.get_sites():
        if options.site_id and options.site_id != site.id:
            continue

        site_folder = os.path.join(options.folder, site.hostname)
        logging.info("Creating folder '%s' for site '%s'" % (site_folder, site.id))
        if not os.path.exists(site_folder):
            os.makedirs(site_folder)
                    
        # create a private folder in case they have private posts
        private_folder = os.path.join(site_folder, "private")
        if not os.path.exists(private_folder):
            os.mkdir(private_folder)

        site_file = os.path.join(site_folder, 'site-%s.json' % site.hostname)
        logging.debug(u"Opening file '%s' for site '%s' (%s)" % 
                      (site_file, site.hostname, site.id))

        with open(site_file, 'w+') as sf:
            simplejson.dump(site, sf, cls=JsonDateEncoder)
            
        rem = 2 if site.num_posts % options.batch_size > 0 else 1
        page_numbers = range(1, int(site.num_posts/options.batch_size) + rem)

        for page in page_numbers:
            logging.info("Retrieving page %s of %s with %s posts per page" % 
                         (page, len(page_numbers), options.batch_size))
            
            for p in posterous.get_posts(site_id=site.id, page_num=page, 
                                         num_posts=options.batch_size):
                post_slug = re.sub(r'^/', '', urlparse.urlparse(p.link).path)
                post_file = os.path.join(site_folder, '%s.json' % post_slug)
            
                logging.debug(u"Opening file '%s' for post '%s'" % 
                              (post_file, p.title))

                with open(post_file, 'w+') as f:
                    simplejson.dump(p, f, cls=JsonDateEncoder)
                
                # save the media from each post
                for i, m in enumerate(p.media):
                    u = m.medium_url if hasattr(m, 'medium_url') else m.url
                    media_type = re.search(r'\.(\w+)$', u).group(1)
                    media_file = os.path.join(site_folder, '%s_%s.%s' % 
                                              (post_slug, i, media_type))                
                    logging.debug("Getting media for post '%s' from url '%s'" %
                                  (p.title, u))
                
                    urllib.urlretrieve(u, media_file)
