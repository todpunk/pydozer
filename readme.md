# pydozer
Simplistic static site generator in Python

# Usage
Clone the repo and add it to your PYTHONPATH, and in case you don't have the required packages:
 pip install -r requirements.txt

Then from your content directory (where you have your configfile.py) run something like the following:
 python /path/to/pydozer.py --conf configfile.py

If you do not specify a config file, it will assume you want the simple_config.py which will likely build the example site. 

# Why another site generator?
I don't want to have to learn an entire tech stack just to spit out some HTML files.  I'm trying to save work from hand-editing something, but all the site generators I've looked at (which are many) are just full of edge cases.  So if I'm going to have to go through the effort, I might as well write something straight forward and simple for my needs.

If that matches your needs too, great.  If not, I'm still time ahead, and I get to make stuff.

# Features/Requirements (when it's done)
- Pages and Blog Posts, parsed separately
- Single point of configuration
- No complicated templating formats (unless jinja2 is complicated)
- The ability to put arbitrary HTML/Javascript in any given page/post
- Static "extra" files such as images or CSS, all in one place, including favicon
- Single build folder as output
- Copy the build folder to root or a subdir in your server
- "Preview" ability, probably through a static file watcher that regenerates the preview folder
- Simple server for said preview
- Meta tags are hierarchial.  There is a global set, and they can all be overridden by page (like titles)
 - We get this almost for free if we use the templating engine appropriately
- Extra javascript includes in header or footer on a per page basis

# Status
Completely usable.  We're using it in more and more generated sites now, and we'd love to hear if you run into any snags.
