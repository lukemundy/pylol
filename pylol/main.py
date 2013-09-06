# encoding: utf-8
import sys
import argparse
import random
import pytz
import dateutil.parser
from time import time
from datetime import datetime

import config

from .api import Api
from .db import db_connect
from .db.tables import *

from sqlalchemy.orm.exc import NoResultFound

def init():
    '''Initialises the PyLoL database by creating all required tables'''

    args = get_args()
    engine, session = db_connect(args.db)

    metadata.create_all(engine)

def update():
    '''Update the database with fresh data from the API'''

    args = get_args()
    api = Api(args.key)

    print 'Connecting to database'
    engine, session = db_connect(args.db)

    q = session.query(Summoner)\
        .join(GroupMem, Group)\
        .filter(Summoner.lastUpdate < (time() - 1800))

    if args.group is not 'all':
        q = q.filter(Group.internalName == args.group)

    summoners = q.all()

    print '%d summoners to update' % len(summoners)

    # Shuffle the summoners so they aren't always updated in the same order
    random.shuffle(summoners)

    for s in summoners:
        print 'Starting update of %s.%s' % (s.name, s.region)

        session.begin(subtransactions=True)

        print 'Fetching match history'
        summoner, games = api.get_match_history(s.name, s.region)

        summoner['lastUpdate'] = int(time())
        s.update_values(summoner)
        session.commit()

        print 'Adding %d matches to database' % len(games['gameStatistics']['array'])

        for g in games['gameStatistics']['array']:
            print 'gameId: %s, userId: %s' % (g['gameId'], g['userId'])

            # Convert the date string in createDate into a unix timestamp
            g['createDate'] = datestr2unix(g['createDate'])

            # Check if game is already in database
            try:
                session.query(Game)\
                .filter_by(gameId = g['gameId'], userId = g['userId'])\
                .one()
            except NoResultFound:
                session.add(Game(s.region, g))
                session.commit()

                session.add(Stat(g['gameId'], g['userId'], g['statistics']['array']))
                session.commit()

                # Add players from this game
                for p in g['fellowPlayers']['array']:
                    try:
                        session.query(Player)\
                        .filter_by(gameId=g['gameId'],
                                   summonerId=p['summonerId'])\
                        .one()
                    except NoResultFound:
                        session.add(Player(g['gameId'], p))
                        session.commit()

                print 'done'
            else:
                print 'Skipping...'

        print 'Finished updating %s.%s' % (s.name, s.region)

    print 'Total API requests: %d' % api.num_requests

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
    ap.add_argument('group', metavar='GROUP', nargs='?', default='all',
                    help='Which group of summoners to update.')

    args = ap.parse_args()

    if args.version:
        import pkg_resources

        print 'PyLoL v%s by Epic Boak <http://epicftw.com/>' % \
            pkg_resources.require('Pylol')[0].version
        sys.exit()

    return args

def datestr2unix(dstr):
    '''Converts a PST/PDT date string from the API into a UTC Unix timestamp.'''

    tz = dstr[-3:]

    if tz == 'PST':
        dstr = dstr[:-3] + '-0800'
    elif tz == 'PDT':
        dstr = dstr[:-3] + '-0700'
    else:
        raise Exception('Invalid timezone "%s" in date string "%s".' % (tz, dstr))

    return int(dateutil.parser.parse(dstr).astimezone(pytz.utc).strftime('%s'))
