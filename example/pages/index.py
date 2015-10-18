# -*- coding: utf-8 -*-
import os
from pydozer import Page
from test import test_page

index_page = Page()
index_page.data['filename'] = os.path.basename(__file__).replace('.pyc', '').replace('.py', '')

index_page.data['title'] = "Welcome to This Land"
index_page.data['content'] = """
    <p>This should be the main page.  Check it out!</p>
    <p>Linking to <a href="%s.html">Test</a> and <a href="%s">the blog listing</a></p>
""" % (test_page.data['filename'], '/blog/listing1.html')
