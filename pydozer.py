import argparse

from flask import Flask
import os
import jinja2
from pprint import pprint
import importlib
import shutil
from gconf import simple_config

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
        simple_config.update(config_module.simple_config)


templateDir = simple_config['templates_dir']
templateLoader = jinja2.FileSystemLoader(searchpath=templateDir)
templateEnv = jinja2.Environment( loader=templateLoader )


class Page(object):
    def __init__(self):
        from gconf import all_pages
        all_pages.append(self)
        self.filename = 'badpage' + simple_config['default_extension']
        self.data = {'config': simple_config['page_config'],
                     'content': ''}


class BlogPost(object):
    def __init__(self):
        from gconf import all_blog_posts
        all_blog_posts.append(self)
        self.filename = 'badblogpost' + simple_config['default_extension']
        self.data = {'config': simple_config['blog_config'],
                     'content': '',
                     }


app = Flask(__name__, static_folder=simple_config['output_dir'], static_url_path='')


@app.route('/hello')
def hello_world():
    return 'Hello World!'


def generate_pages():
    """
    We go through all the possibilities for generating any page related details
    """
    from gconf import all_pages
    template = templateEnv.get_template(simple_config['page_config']['page_default_template'])
    for page in all_pages:
        page_template = template
        file_ext = simple_config['default_extension']
        # If we override the template for that page, here it gets invoked
        if 'template' in page.data:
            page_template = templateEnv.get_template(page.data['template'])
        # Same with file extension, which opens some nice scripting possibilities
        if 'extension' in page.data:
            file_ext = page.data['extension']
        output_filename = os.path.join(simple_config['output_dir'] + '/' + page.filename + file_ext)
        with open(output_filename, 'w+') as f:
            f.write(page_template.render(page.data))


def generate_blog_posts():
    """
    We go through all blog posts and their related optional outputs like tags or authors, depending on config
    """
    raise NotImplementedError


def generate_extras():
    """
    EVERY site should have extra files, even if it's just CSS or JS files, so process them here very simply
    """
    from gconf import simple_config
    extra_files_dir = os.path.join(simple_config['content_dir'], 'extra_files')
    if 'extras_output_dir' in simple_config:
        output_dir = os.path.join(simple_config['extras_output_dir'])
    else:
        output_dir = os.path.join(simple_config['output_dir'])
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    shutil.copytree(extra_files_dir, output_dir)


if __name__ == '__main__':
    if build:
        print('Well, we should build here I guess')
        from example.pages import *
        from example.blog_posts import *
        from gconf import all_blog_posts, all_pages
        if os.path.exists(simple_config['output_dir']):
            shutil.rmtree(simple_config['output_dir'])
            os.makedirs(simple_config['output_dir'])
        generate_extras()
        generate_pages()
    if preview:
        print('We will run a server here when we can serve things')
        #app.run()


