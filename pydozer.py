import argparse

from flask import Flask
import os
from pprint import pprint
import importlib


# Argument handling
parser = argparse.ArgumentParser(
    description='Work with site generation or previewing, by default doing both build and preview')
parser.add_argument('-b', '--build', help='Generate the site from its sources (deleting any current build)',
                    default=False, action="store_true")
parser.add_argument('-p', '--preview', help='Preview the currently built site by running a web server',
                    default=False, action="store_true")
parser.add_argument('-c', '--config', help='This should be a config python module',
                    default='simple_config')


build = True
preview = True

if __name__ == '__main__':
    args = parser.parse_args()
    if args.preview and (not args.build):
        build = False
    config_file = args.config
    # This needs to either always end in .py and be stripped afterward, or stripped now and assumed to be without it
    # we opt for the latter, they're both messy.
    if config_file.endswith('.py'):
        config_file.replace('.py', '')
    if not os.path.isfile(config_file+'.py'):
        print('config file required to exist and by a .py file, given: %s' % config_file+'.py')
        exit(1)
    else:
        config_module = importlib.import_module(config_file)
        from gconf import simple_config
        simple_config.update(config_module.simple_config)


class Page(object):
    def __init__(self):
        from gconf import all_pages, simple_config
        all_pages.append(self)
        self.data = {'title': simple_config['site_title'],
                     'content': ''}


class BlogPost(object):
    def __init__(self):
        from gconf import all_blog_posts, simple_config
        all_blog_posts.append(self)
        self.data = {'title': simple_config['blog_title'],
                     'content': '',
                     }


app = Flask(__name__, static_folder='/', static_url_path='/')


@app.route('/hello')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    if build:
        print('Well, we should build here I guess')
        from example.pages import *
        from example.blog_posts import *
        from gconf import all_blog_posts, all_pages, simple_config
        pprint(simple_config)
    if preview:
        print('We will run a server here when we can serve things')
        # app.run()


