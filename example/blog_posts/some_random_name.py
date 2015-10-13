# -*- coding: utf-8 -*-
import os
import dateutil.parser
from pydozer import BlogPost
from slugify import slugify

a_post = BlogPost()

# These are all optional
a_post.author = 'Tod Hansmann'
a_post.tags = ['generated', 'third']

# These are not optional at all
a_post.posted_date = dateutil.parser.parse('Sun Sep 28 9:36:28 MST 2003')
a_post.data['title'] = 'This is the fourth post'
a_post.filename = slugify(unicode(a_post.data['title']))
a_post.data['content'] = """
<p>Third post, hopefully an hour ahead of the fourth.</p>
"""
