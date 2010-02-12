"""
    needs python 2.6
"""

from __future__ import with_statement
from optparse import OptionParser
import logging 
import datetime
import os, os.path
import re
import urlparse, urllib
import simplejson

from posterous import Posterous


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
                site.json
                {post-slug}.json  <-- contains body & comments & everything else
                {post-slug}_media{num}
    """
    
    opt_parser = OptionParser()
    opt_parser.add_option("-u", "--username", dest="username", help="Email address associated with posterous account")
    opt_parser.add_option("-p", "--password", dest="password", help="Password associated with posterous account")
    opt_parser.add_option("-f", "--folder", dest="folder", help="Folder to store backup data in (Beware, if it exists, data may be overwritten)")
    opt_parser.add_option("-s", "--site-id", dest="site_id", help="Only query site with this id")
    opt_parser.add_option("-d", "--debug", dest="debug", action="store_true", default=False, help="Debug output")
    opt_parser.add_option("-v", "--verbose", dest="verbose", action="store_true", default=False, help="Verbose output (overrides -d)")
    opt_parser.add_option("-q", "--quiet", dest="quiet", action="store_true", default=True, help="Quiet output (overrides -v and -d)")
    (options, args) = opt_parser.parse_args()
    
    if options.debug:
        logging.basicConfig(level=logging.DEBUG)
    elif options.verbose:
        logging.basicConfig(level=logging.INFO)
    elif options.quiet:
        logging.basicConfig(level=logging.WARNING)
        
    posterous = Posterous(options.username, options.password)
    for site in posterous.get_sites():
        if options.site_id and options.site_id != site.id:
            continue
        site_folder = os.path.join(options.folder, site.hostname)
        logging.info("Creating folder '%s' for site '%s'" % (site_folder, site.id))
        if not os.path.exists(site_folder):
            os.makedirs(site_folder)
        for p in posterous.get_posts(site.id):
            post_slug = re.sub(r'^/', '', urlparse.urlparse(p.link).path)
            post_file = os.path.join(site_folder, '%s.json' % post_slug)
            
            logging.debug(u"Opening file '%s' for post '%s'" % (post_file, p.title))
            with open(post_file, 'w+') as f:
                simplejson.dump(p, f, cls=JsonDateEncoder)
                
            for i, m in enumerate(p.media):
                u = m.medium_url if hasattr(m, 'medium_url') else m.url
                media_type = re.search(r'\.(\w+)$', u).group(1)
                media_file = os.path.join(site_folder, '%s_%s.%s' % (post_slug, i, media_type))                
                logging.debug("Getting media for post '%s' from url '%s'" % (p.title, u))
                
                urllib.urlretrieve(u, media_file)
