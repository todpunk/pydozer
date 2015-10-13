# -*- coding: utf-8 -*-
import os
import dateutil.parser
from pydozer import BlogPost
from slugify import slugify

first_post = BlogPost()

# These are all optional
first_post.author = 'Tod Hansmann'
first_post.tags = ['first', 'testing', 'generated']
first_post.data['never_used'] = 'This is never actually used, but I can throw it in for later use if I want'

# These are not optional at all
first_post.posted_date = dateutil.parser.parse('Thu Sep 25 10:36:28 MST 2003')
first_post.data['title'] = 'Test Blog Up and Running'
first_post.filename = slugify(unicode(first_post.data['title']))
first_post.data['content'] = """
<p>This should be our first post.  I could technically generate this or manipulate it after the fact, or use part of it, or mix it up <b>with HTML</b> if I want.</p>
<p>Really anything I want, as complex as I want, anywhere in python's vast libraries, or just leave it simple.</p>
<p>For instance we're using slugify to make SEO friendly URLs, but that's not required.  Just whatever will give us python datetimes for posted_dates and a filename</p>
"""
