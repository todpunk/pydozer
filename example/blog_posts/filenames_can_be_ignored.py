# -*- coding: utf-8 -*-
import os
import dateutil.parser
from pydozer import BlogPost
from slugify import slugify

a_post = BlogPost()

# These are all optional
a_post.data['author'] = 'Not Tod'
a_post.data['tags'] = ['testing', 'generated', 'fourth']

# These are not optional at all
a_post.data['posted_date'] = dateutil.parser.parse('Sun Sep 28 10:36:28 MST 2003')
a_post.data['title'] = 'This is the fourth post'
a_post.data['filename'] = slugify(unicode(a_post.data['title']))
a_post.data['content'] = """
<p>I'm reusing the object's name because it absolutely does not matter.</p>
"""
