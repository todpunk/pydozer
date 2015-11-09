# -*- coding: utf-8 -*-
import argparse
import datetime

from flask import Flask, make_response
import mimetypes
import os
import jinja2
import dateutil.parser
import math
from pprint import pprint
import importlib
import shutil
from gconf import simple_config
from functools import update_wrapper

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
    if args.build and (not args.preview):
        preview = False
    config_file = args.config
    # This needs to either always end in .py and be stripped afterward, or stripped now and assumed to be without it
    # we opt for the latter, they're both messy.
    if config_file.endswith('.py'):
        config_file = config_file.replace('.py', '')
    if not os.path.isfile(config_file+'.py'):
        print('config file required to exist and be a .py file, given: %s' % config_file+'.py')
        exit(1)
    else:
        config_module = importlib.import_module(config_file)
        simple_config.update(config_module.simple_config)


templateDir = simple_config['templates_dir']
templateLoader = jinja2.FileSystemLoader(searchpath=templateDir)
templateEnv = jinja2.Environment( loader=templateLoader )
mimetypes.add_type('text/html', simple_config['default_extension'])


class Page(object):
    def __init__(self):
        from gconf import all_pages
        all_pages.append(self)
        self.data = {'filename': 'badpage' + simple_config['default_extension'],
                     'config': simple_config['page_config'],
                     'content': ''}

    def __repr__(self):
        return self.data['filename']


class BlogPost(object):
    def __init__(self):
        from gconf import all_blog_posts
        all_blog_posts.append(self)
        self.posted_date = datetime.datetime.now()
        self.data = {'filename': 'badblogpost' + simple_config['default_extension'],
                     'config': simple_config['blog_config'],
                     'content': '',
                     'title': 'default_title',
                     }

    def __repr__(self):
        return self.data['filename']


app = Flask(__name__, static_folder=simple_config['output_dir'], static_url_path='')


def nocache(f):
    def new_func(*args, **kwargs):
        resp = make_response(f(*args, **kwargs))
        resp.cache_control.no_cache = True
        return resp
    return update_wrapper(new_func, f)


@app.after_request
def nocache_response(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Expires'] = '-1'
    return response


@app.route('/hello')
def hello_world():
    return 'Hello World!'


@app.route('/')
@nocache
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
        output_filename = os.path.join(simple_config['output_dir'] + '/' + page.data['filename'] + file_ext)
        with open(output_filename, 'w+') as f:
            f.write(page_template.render(page.data))


def generate_blog_posts():
    """
    We go through all blog posts and their related optional outputs like tags or authors, depending on config
    """
    from gconf import all_blog_posts
    all_blog_posts.sort(key=lambda post: post.data['posted_date'], reverse=simple_config.get('descending', True))
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
    all_posts_list = [x.data for x in all_blog_posts]
    for blog_post in all_blog_posts:
        post_template = blog_template
        post_ext = file_ext
        # If we override the template for that page, here it gets invoked
        if 'template' in blog_post.data:
            page_template = templateEnv.get_template(blog_post.data['template'])
        # I don't know why this would be useful, but it's the same code, so whatever
        if 'extension' in blog_post.data:
            post_ext = blog_post.data['extension']
        output_filename = os.path.join(output_dir, blog_post.data['filename'] + post_ext)
        with open(output_filename, 'w+') as f:
            blog_post.data['all_posts'] = all_posts_list
            f.write(post_template.render(blog_post.data))

        # Now populate lists, first one only if the post has all the keys needed for a listing
        if listing_template and set(blog_config['listing_keys_needed']).issubset(blog_post.data.keys()):
            listings.append(blog_post.data)
        # Make a list of posts for each tag out there
        if tags_template and tag_template and blog_post.data.get('tags'):
            for tag in blog_post.data['tags']:
                if tag not in tags:
                    tags[tag] = []
                tags[tag].append(blog_post.data)
        # Make a list of posts for each author out there
        if authors_template and author_template and blog_post.data.get('author'):
            if blog_post.data['author'] not in authors:
                authors[blog_post.data['author']] = []
            authors[blog_post.data['author']].append(blog_post.data)

    # Make them templates objects
    if listing_template:
        listing_template = templateEnv.get_template(listing_template)
    if tags_template and tag_template:
        tags_template = templateEnv.get_template(tags_template)
        tag_template = templateEnv.get_template(tag_template)
    if authors_template and author_template:
        authors_template = templateEnv.get_template(authors_template)
        author_template = templateEnv.get_template(author_template)

    if listing_template:
        if 'listing_pagination_num' in blog_config:
            page_limit = blog_config['listing_pagination_num']
            total_pages = int(math.floor(len(listings) / page_limit) + 1)
            ranges = range(1,  total_pages + (total_pages > 1)) or [1]
            for page_num in ranges:
                file_num = str(page_num) + file_ext
                offset = (page_num - 1) * page_limit
                output_filename = os.path.join(output_dir, 'listing' + file_num)
                with open(output_filename, 'w+') as f:
                    f.write(listing_template.render({'posts': listings[offset:offset+page_limit],
                                                     'all_posts': all_posts_list,
                                                     'title': blog_config['title'],
                                                     'page_num': page_num,
                                                     'total_pages': total_pages}))
        else:
            output_filename = os.path.join(output_dir, 'listing' + file_ext)
            with open(output_filename, 'w+') as f:
                f.write(listing_template.render({'posts': listings,
                                                 'all_posts': all_posts_list,
                                                 'title': blog_config['title']}))

    if tags_template and tag_template:
        output_filename = os.path.join(output_dir, 'tags' + file_ext)
        with open(output_filename, 'w+') as f:
            f.write(tags_template.render({'tags': tags, 'title': 'Tags', 'all_posts': all_posts_list}))
        for tag, posts in tags.iteritems():
            if 'tag_pagination_num' in blog_config:
                page_limit = blog_config['tag_pagination_num']
                total_pages = int(math.floor(len(posts) / page_limit)) + 1
                ranges = range(1,  total_pages + (total_pages > 1)) or [1]
                for page_num in ranges:
                    file_num = str(page_num) + file_ext
                    offset = (page_num - 1) * page_limit
                    tag_file = 'tag_' + tag.replace(' ', '_')
                    output_filename = os.path.join(output_dir, tag_file + file_num)
                    with open(output_filename, 'w+') as f:
                        f.write(tag_template.render({'posts': posts[offset:offset+page_limit],
                                                     'all_posts': all_posts_list,
                                                     'tag': tag,
                                                     'tag_file': tag_file,
                                                     'title': 'Posts for tag: ' + tag,
                                                     'page_num': page_num,
                                                     'total_pages': total_pages}))
            else:
                output_filename = os.path.join(output_dir, 'tag_' + tag.replace(' ', '_') + file_ext)
                with open(output_filename, 'w+') as f:
                    f.write(tag_template.render({'posts': posts,
                                                 'all_posts': all_posts_list,
                                                 'tag': tag,
                                                 'title': 'Posts for tag: ' + tag}))

    if authors_template and author_template:
        output_filename = os.path.join(output_dir, 'authors' + file_ext)
        with open(output_filename, 'w+') as f:
            f.write(authors_template.render({'authors': authors, 'title': 'Authors', 'all_posts': all_posts_list}))
        for author, posts in authors.iteritems():
            if 'author_pagination_num' in blog_config:
                page_limit = blog_config['author_pagination_num']
                total_pages = int(math.floor(len(posts) / page_limit) + 1)
                ranges = range(1,  total_pages + (total_pages > 1)) or [1]
                for page_num in ranges:
                    file_num = str(page_num) + file_ext
                    offset = (page_num - 1) * page_limit
                    author_file = 'author_' + author.replace(' ', '_')
                    output_filename = os.path.join(output_dir, author_file + file_num)
                    with open(output_filename, 'w+') as f:
                        f.write(author_template.render({'author': author,
                                                        'author_file': author_file,
                                                        'title': 'Posts for author: ' + author,
                                                        'posts': posts[offset:offset+page_limit],
                                                        'all_posts': all_posts_list,
                                                        'page_num': page_num,
                                                        'total_pages': total_pages}))
            else:
                output_filename = os.path.join(output_dir, 'author_' + author.replace(' ', '_') + file_ext)
                with open(output_filename, 'w+') as f:
                    f.write(author_template.render({'author': author,
                                                    'all_posts': all_posts_list,
                                                    'title': 'Posts for author: ' + author,
                                                    'posts': posts}))


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
        from gconf import all_blog_posts, all_pages
        pages = importlib.import_module(os.path.basename(simple_config['content_dir'])+'.pages')
        blog_posts = importlib.import_module(os.path.basename(simple_config['content_dir'])+'.blog_posts')
        if os.path.exists(simple_config['output_dir']):
            shutil.rmtree(simple_config['output_dir'])
            os.makedirs(simple_config['output_dir'])
        generate_extras()
        generate_pages()
        generate_blog_posts()
    if preview:
        app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 5
        app.run(host='0.0.0.0')


