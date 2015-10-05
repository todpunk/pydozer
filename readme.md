# pydozer
Simplistic static site generator in Python

# Why another site generator?
I don't want to have to learn an entire tech stack just to spit out some HTML files.  I'm trying to save work from hand-editing something, but all the site generators I've looked at (which are many) are just full of edge cases.  So if I'm going to have to go through the effort, I might as well write something straight forward and simple for my needs.

If that matches your needs too, great.  If not, I'm still time ahead, and I get to make stuff.

# Features/Requirements (when it's done)
- Pages and Blog Posts, parsed separately
- Single point of configuration
- No complicated templating formats
- The ability to put arbitrary HTML/Javascript in any given page/post
- Static "extra" files such as images or CSS, all in one place
- Single build folder as output
- Copy the build folder to root or a subdir in your server
- "Preview" ability, probably through a static file watcher that regenerates the preview folder
- Simple server for said preview
- Meta tags are hierarchial.  There is a global set, and they can all be overridden by page (like titles)
- Extra javascript includes in header or footer on a per page basis

# Status
Not even close yet.  Probably a few days out.