from flask import Flask
import argparse


app = Flask(__name__, static_folder='/', static_url_path='/')

# Argument handling
parser = argparse.ArgumentParser(
    description='Work with site generation or previewing, by default doing both build and preview')
parser.add_argument('-b', '--build', help='Generate the site from its sources (deleting any current build)',
                    default=False, action="store_true")
parser.add_argument('-p', '--preview', help='Preview the currently built site by running a web server',
                    default=False, action="store_true")


@app.route('/hello')
def hello_world ():
    return 'Hello World!'


if __name__ == '__main__':
    args = parser.parse_args()
    print args.preview
    build = True
    preview = True
    if args.preview and (not args.build):
        build = False
    if build:
        print('Well, we should build here I guess')
    if preview:
        print('We will run a server here when we can serve things')
        # app.run()
