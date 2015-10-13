import json
import os


this_dir = os.path.join(__file__.replace(os.path.basename(__file__), ''))
# We just shove this in a json object, note that many of these are defaults and can be overridden by page/post
config_raw = \
{
    "content_dir": os.path.join(this_dir, "example"),
    "output_dir": os.path.join(this_dir, "generated"),
    "templates_dir": os.path.join(this_dir, "templates"),
    "site_title": "This Site's Default Title",
    "default_extension": ".html",
    "page_config": {
        "page_title": "This Site's Title",
        "page_default_template": "page.jinja2"
    },
    "blog_config": {
        "title": "This Blog's Title",
        "blog_base_dir": "/blog",
        "blog_template": "blog.jinja2",
        "listing_template": "listing.jinja2",
        "tags_template": "tags.jinja2",
        "authors_template": "authors.jinja2"
    }
}

# This is separate so we have one end point, but we can generate it however we want above, this is just an example
simple_config = config_raw

