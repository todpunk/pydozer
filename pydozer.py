# -*- coding: utf-8 -*-
import argparse
import datetime

from flask import Flask
import os
import jinja2
import dateutil.parser
import math
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
        self.posted_date = datetime.datetime.now()
        self.filename = 'badblogpost' + simple_config['default_extension']
        self.data = {'config': simple_config['blog_config'],
                     'content': '',
                     }


app = Flask(__name__, static_folder=simple_config['output_dir'], static_url_path='')


@app.route('/hello')
def hello_world():
    return 'Hello World!'


@app.route('/')
def root():
    return app.send_static_file(simple_config['start_page'])


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
    from gconf import all_blog_posts
    all_blog_posts.sort(key=lambda post: post.posted_date, reverse=True)
    blog_config = simple_config['blog_config']
    blog_template = templateEnv.get_template(blog_config['blog_template'])
    listing_template = blog_config.get('listing_template')
    listings = []
    tags_template = blog_config.get('tags_template')
    tag_template = blog_config.get('tag_template')
    tags = {}
    authors_template = blog_config.get('authors_template')
    author_template = blog_config.get('author_template')
    authors = {}
    output_dir = os.path.join(simple_config['output_dir'], blog_config['blog_base_dir'])
    file_ext = simple_config['default_extension']
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # We'll need to make all the blog posts and add to our other lists as we go
    for blog_post in all_blog_posts:
        post_template = blog_template
        post_ext = file_ext
        # We need this only for links
        blog_post.data['filename'] = blog_post.filename
        # If we override the template for that page, here it gets invoked
        if 'template' in blog_post.data:
            page_template = templateEnv.get_template(blog_post.data['template'])
        # I don't know why this would be useful, but it's the same code, so whatever
        if 'extension' in blog_post.data:
            post_ext = blog_post.data['extension']
        output_filename = os.path.join(output_dir, blog_post.filename + post_ext)
        with open(output_filename, 'w+') as f:
            f.write(post_template.render(blog_post.data))

        # Now populate lists, first one only if the post has all the keys needed for a listing
        if listing_template and set(blog_config['listing_keys_needed']).issubset(blog_post.data.keys()):
            listings.append(blog_post.data)
        # Make a list of posts for each tag out there
        if tags_template and tag_template and hasattr(blog_post, 'author'):
            for tag in blog_post.tags:
                if tag not in tags:
                    tags[tag] = []
                tags[tag].append(blog_post.data)
        # Make a list of posts for each author out there
        if authors_template and author_template and hasattr(blog_post, 'author'):
            if blog_post.author not in authors:
                authors[blog_post.author] = []
            authors[blog_post.author].append(blog_post.data)

    # Make them templates objects
    if listing_template:
        listing_template = templateEnv.get_template(listing_template)
    if tags_template and tag_template:
        tags_template = templateEnv.get_template(tags_template)
        tag_template = templateEnv.get_template(tag_template)
    if authors_template and author_template:
        authors_template = templateEnv.get_template(authors_template)
        author_template = templateEnv.get_template(author_template)

    # Note that we're not paginating yet.
    # TODO: Pagination of some kind for some things?
    if listing_template:
        output_filename = os.path.join(output_dir, 'listing' + file_ext)
        with open(output_filename, 'w+') as f:
            f.write(listing_template.render({'listings': listings}))

    if tags_template and tag_template:
        output_filename = os.path.join(output_dir, 'tags' + file_ext)
        with open(output_filename, 'w+') as f:
            f.write(tags_template.render(tags))
		for tag, posts in tags.iteritems():
			if 'tag_pagination_num' in blog_config:
				page_limit = blog_config['tag_pagination_num']
				ranges = range(1, math.floor(len(posts) / page_limit) + ((len(posts) / page_limit) > 1) + 1
				for page_num in ranges:
					file_num = str(page_num)
					offset = (page_num - 1) * page_limit
					output_filename = os.path.join(output_dir, tag + file_num + file_ext)
					with open(output_filename, 'w+') as f:
						f.write(tag_template.render({tag: posts[offset:offset+page_limit]}))
			else:
				output_filename = os.path.join(output_dir, tag + file_ext)
				with open(output_filename, 'w+') as f:
					f.write(tag_template.render({tag: posts}))

    if authors_template and author_template:
        output_filename = os.path.join(output_dir, 'authors' + file_ext)
        with open(output_filename, 'w+') as f:
            f.write(authors_template.render(authors))
        for author, posts in authors.iteritems():
            output_filename = os.path.join(output_dir, author + file_ext)
            with open(output_filename, 'w+') as f:
                f.write(author_template.render({author: posts}))


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
    # This needs to be removed even though output's removed in the main script, because it COULD be different here
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
        generate_blog_posts()
    if preview:
        print('We will run a server here when we can serve things')
        app.run()


