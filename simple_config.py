import json
import os


this_dir = os.path.join(__file__.replace(os.path.basename(__file__), '')).replace('\\', '\\\\')
# We just shove this in a json object
config_raw = """
{
    "content_dir": "%(this_dir)sexample",
    "output_dir": "%(this_dir)sgenerated",
    "templates_dir": "%(this_dir)stemplates",
    "site_title": "This Site's Title",
    "blog_title": "This Blog's Title"
}
""" % {'this_dir': this_dir}
print(config_raw)
simple_config = json.loads(config_raw)

