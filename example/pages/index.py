# -*- coding: utf-8 -*-
import os
from pydozer import Page

index_page = Page()
index_page.filename = os.path.basename(__file__).replace('.pyc', '').replace('.py', '')

index_page.data['title'] = "Welcome to This Land"
index_page.data['content'] = """
    <p>This should be the main page.  Check it out!</p>
"""
