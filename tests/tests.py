
import sys
sys.path.append("..")

from datetime import datetime 
import os.path
import posterous


def get_file_name(n):
    return os.path.join(os.path.dirname( os.path.realpath( __file__ ) ), n)


def test_sites_xml_parser():
    with open(get_file_name('sites.xml')) as f:
        sites = posterous.parse_sites_xml(f.read())
        
        assert len(sites) == 2
        assert sites[0].name == "Sachin Agarwal's Posterous"
        assert sites[0].hostname == 'sachin'
        assert sites[0].url == 'http://sachin.posterous.com'
        assert sites[0].id == 1
        assert sites[0].private == False
        assert sites[0].primary == True
        assert sites[0].commentsenabled == True
        assert sites[0].num_posts == 50        
        
        
def test_post_xml_parser():
    with open(get_file_name('posts.xml')) as f:
        posts = posterous.parse_posts_xml(f.read())
        
        assert len(posts) == 4, "List length is %s" % len(posts)
        p = posts[0]
        assert p.url == 'http://post.ly/abc123'
        assert p.title == 'Brunch in San Francisco'
        assert p.id == 55
        assert p.views == 0
        assert p.body == "What a great brunch!"
        assert p.private == False
        assert p.commentsenabled == True
        assert p.link == 'http://sachin.posterous.com/brunch-in-san-francisco'
        assert p.authorpic == 'http://debug2.posterous.com/user_profile_pics/16071/Picture_1_thumb.png'
        assert p.date == posterous.parse_date('Sun, 03 May 2009 19:58:58 -0800')
        
        assert len(p.comments) == 1
        assert p.comments[0].body == 'This is a comment'
        assert p.comments[0].author == 'sachin'
        assert p.comments[0].date == posterous.parse_date('Thu, 04 Jun 2009 01:33:43 -0800')
        
        assert len(p.media) == 3
        img = p.media[0]
        aud = p.media[1]
        vid = p.media[2]
        
        assert img.medium_filesize == 47
        assert img.medium_url == 'http://posterous.com/getfile/files.posterous.com/sachin/DIptatiCkiv/IMG_0477.scaled500.jpg'
        assert img.medium_width == 500
        assert img.medium_height == 333
        assert img.thumb_url == 'http://posterous.com/getfile/files.posterous.com/sachin/DIptatiCkiv/IMG_0477.thumb.jpg'
        assert img.thumb_filesize == 5
        assert img.thumb_height == 36
        assert img.thumb_width == 36
        
        assert aud.url == "http://posterous.com/getfile/files.posterous.com/sachin/DIptatiCkiv/sheila.mp3"
        assert aud.filesize == 10116
        assert aud.artist == 'Smashing Pumpkins'
        assert aud.album == 'Adore'
        assert aud.song == "To Sheila"
        
        assert vid.url == "http://posterous.com/getfile/files.posterous.com/sachin/DIptatiCkiv/movie.avi"
        assert vid.filesize == 6537
        assert vid.thumb == "http://posterous.com/getfile/files.posterous.com/sachin/DIptatiCkiv/movie.png"
        assert vid.flv == "http://posterous.com/getfile/files.posterous.com/sachin/DIptatiCkiv/movie.flv"
        assert vid.mp4 == "http://posterous.com/getfile/files.posterous.com/sachin/DIptatiCkiv/movie.mp4"
        
    