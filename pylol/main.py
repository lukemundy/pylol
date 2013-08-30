# encoding: utf-8
import sys
import argparse

import config

from .api import Api
from .db import db_connect

def init():
    '''Initialises the PyLoL database by creating all required tables'''

    args = get_args()
    api = Api(args.key)
    db, meta, session = db_connect(args.db, True)

def update():
    '''Update the database with fresh data from the API'''

    args = get_args()
    api = Api(args.key)
    db, meta, session = db_connect(args.db)

    print api


### Helper functions

def get_args():
    '''Creates an argparse object and the standard global options.'''

    ap = argparse.ArgumentParser(description='Interact with data from the '
        'Mashape League of Legends API.', epilog='Written by Luke Mundy '
        '<lmundy@gmail.com>'
    )

    ap.add_argument('-q', '--quiet', action='store_true', help='Supresses all '
                    'console output.')
    ap.add_argument('-v', '--version', action='store_true', help='Print the '
                    'current Pylol version and exit.')
    ap.add_argument('-d', '--db', metavar='URI', default=config.default_uri,
                    help='Use the database specified by URI instead of the '
                    'internal PyLoL db.')
    ap.add_argument('-k', '--key', metavar='KEY', default=config.default_key,
                    help='A valid API key.')

    args = ap.parse_args()

    if args.version:
        import pkg_resources

        print 'PyLoL', pkg_resources.require('Pylol')[0].version
        sys.exit

    return args
