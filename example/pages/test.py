# -*- coding: utf-8 -*-
import os
from pydozer import Page

test_page = Page()
test_page.data['filename'] = os.path.basename(__file__).replace('.pyc', '').replace('.py', '')

test_page.data['title'] = "Test Page"
test_page.data['extra_headers'] = """
    <link rel="stylesheet" href="extra.css" type="text/css" />
    <script type="text/javascript" src="extra.js"></script>
"""
test_page.data['content'] = """
    <p>This should be the second test page.  Check it out!</p> <img src="/zips.gif" />
"""