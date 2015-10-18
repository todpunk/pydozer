# -*- coding: utf-8 -*-
import os
import dateutil.parser
from pydozer import BlogPost
from slugify import slugify
from first_post import first_post

second_post = BlogPost()

# These are all optional
second_post.data['author'] = 'Also Not Tod'
second_post.data['tags'] = ['third', 'testing', 'generated']  # Yes, I tagged it third.
second_post.data['extra_headers'] = """
    <link rel="stylesheet" href="extra.css" type="text/css" />
    <script type="text/javascript" src="extra.js"></script>
"""

# These are not optional at all
second_post.data['posted_date'] = dateutil.parser.parse('Fri Sep 26 20:36:28 MST 2003')
second_post.data['title'] = 'Oh hello, oh hello, second post to you'
second_post.data['filename'] = slugify(unicode(second_post.data['title']))
second_post.data['content'] = """
<p>This should be our second post.  This is how I'm linking to the <a href='%s/%s'>%s</a> (second post for those reading
the template file) and I could do other ways if I wanted.  It's just python.</p>
""" % (second_post.data['config']['blog_base_dir'], first_post.data['filename'], first_post.data['title'])
