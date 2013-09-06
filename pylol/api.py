# encoding: utf8
import urllib
import urllib2
import re
import simplejson as json

class APIExceededRequestLimit(Exception):
    '''Thrown when an request cannot be made due to hitting the API request
    limit'''

    def __init__(self):
        self.msg = u'You have exceeded your daily request limit'

class APIFailure(Exception):
    '''Thrown when an API request returns success = false'''

    def __init__(self, eid, msg, path, url):
        self.eid = eid
        self.msg = msg
        self.path = path
        self.url = url

class APIInvalidData(Exception):
    '''Thrown when the API returns invalid/corrupted JSON data'''

    def __init__(self, data):
        self.msg = u'API returned invalid JSON data.'
        self.data = data

class Api(object):
    '''A wrapper class for pulling data from the `League of Legends Mashape API
    <https://www.mashape.com/meepo/league-of-legends>`_.'''

    # Public vars
    key           = ''  # API key
    num_requests  = 0   # How many API requests have been made
    num_remainreq = -1  # Number of requests remaining today

    # Private vars
    _url     = 'https://bandlecity88c99ea3.p.mashape.com/' # Full URL to the API
    _regions = ('na', 'br', 'euw', 'eun', 'ru', 'tr', 'las', 'lan', 'oc')

    def __init__(self, key):
        '''
        :type key: string
        :param key: API developer key.

        If you do not yet have a developer key to access the API you can
        request a new one from https://www.mashape.com/.'''

        self.key = unicode(key)

    def request(self, path, headers = None):
        '''Send a request to the Elophant API.

        :type path: string
        :param path: Path to the desired API resource.

        :returns: A dictionary containing the decoded JSON data.

        Makes an API request to the given path and returns the decoded JSON as
        a dictionary.

        *path* will have any leading or trailing slash stripped before the
        request is made, so you should not include them if you can avoid it.'''

        # Make sure we have enough requests remaining
        if self.num_remainreq == 0:
            raise APIExceededRequestLimit()

        # Remove slashes from start/end of path
        if path[0] is '/': path = path[1:]
        if path[-1] is '/': path = path[:-1]

        url = '%s%s' % (self._url, path)

        # Make the request
        req = urllib2.Request(url, headers={
            'X-Mashape-Authorization' : self.key
        })

        if headers is not None:
            for key, val in headers.items():
                req.add_header(key, val)

        rsp = urllib2.urlopen(req)

        try:
            data = json.loads(rsp.read())
        except json.JSONDecodeError as e:
            raise APIInvalidData(e.doc)

        if data['success'] is False:
           raise APIFailure(data['eid'], data['error_message'], path, url)
        else:
           self.num_requests += 1;

        return data

    def validate_region(self, region):
        '''Checks that the supplied region is valid

        :type region: string
        :param region: Game region

        :returns: The validated game region'''

        if region is not None:
            region = unicode(region).lower()

        if region not in self._regions:
            raise APIInvalidRegion(region)

        return region

    def get_items(self):
        '''Returns data on each item.

        :returns: A dictionary.

        Refer to https://www.mashape.com/meepo/league-of-legends#!endpoint-Gamedata-Items
        for more information.'''

        return self.request('datadragon/item')

    def get_champions(self):
        '''Returns a dictionary containing information on all champions.

        :returns: A dictionary.

        Refer to https://www.mashape.com/meepo/league-of-legends#!endpoint-Gamedata-Champions
        for more information.'''

        return self.request('datadragon/champion')

    def get_masteries(self):
        '''Returns a dictionary containing information on all masteries and the
        mastery tree.

        :returns: A dictionary.

        Refer to https://www.mashape.com/meepo/league-of-legends#!endpoint-Gamedata-Masteries
        for more information.'''

        return self.request('datadragon/mastery')

    def get_profileicons(self):
        '''Returns a dictionary containing information on all profile icons.

        :returns: A dictionary.

        Refer to https://www.mashape.com/meepo/league-of-legends#!endpoint-Gamedata-Profile-icons
        for more information.'''

        return self.request('datadragon/profileicon')

    def get_runes(self):
        '''Returns a dictionary containing information on all available runes.

        :returns: A dictionary.

        Refer to https://www.mashape.com/meepo/league-of-legends#!endpoint-Gamedata-Runes
        for more information.'''

        return self.request('datadragon/rune')

    def get_summoner_spells(self):
        '''Returns a dictionary containing information on all summoner spells.

        :returns: A dictionary.

        Refer to https://www.mashape.com/meepo/league-of-legends#!endpoint-Gamedata-Summoner-spells
        for more information.'''

        return self.request('datadragon/summoner')

    def get_free_week_champs(self, region):
        '''Returns a dictionary containing information on the current free week
        champions for the specified region.

        :type region: string
        :param region: Game region to check.

        :returns: A dictionary.

        Refer to https://www.mashape.com/meepo/league-of-legends#!endpoint-Service-free-week
        for more information.'''

        region = self.validate_region(region)

        return self.request('service-state/%s/free-week' % region)

    def get_queue_info(self, region):
        '''Returns a dictionary containing information on the matchmaking
        queues for the specified region.

        :type region: string
        :param region: Game region to check.

        :returns: A dictionary.

        Refer to https://www.mashape.com/meepo/league-of-legends#!endpoint-Service-matchmaking-status-detailed-
        for more information.'''

        region = self.validate_region(region)

        return self.request('service-state/%s/matchmaking-queues' % region)

    def get_summoner(self, name, region):
        '''Returns some basic information on a summoner.

        :type name: string
        :param name: The summoner name to search for.

        :type region: string
        :param region: Which game region to search in.

        :returns: A dictionary containing the summoner data.

        Refer to https://www.mashape.com/meepo/league-of-legends#!endpoint-Summoner-basic-information
        for more information.'''

        name = urllib.quote(name)
        region = self.validate_region(region)

        data = self.request('player/%s/%s' % (region, name))['data']

        return data

    def get_summoner_honor(self, name, region):
        '''Returns the amount of honor a summoner has earned.

        :type name: string
        :param name: The summoner name to search for.

        :type region: string
        :param region: Which game region to search in.

        :returns: A dictionary containing the honor data.

        Refer to https://www.mashape.com/meepo/league-of-legends#!endpoint-Summoner-honor-commendations
        for more information.'''

        name = urllib.quote(name)
        region = self.validate_region(region)

        return self.request('player/%s/%s/honor' % (region, name))

    def get_ingame_info(self, name, region):
        '''Returns information about the current game the supplied summoner is
        playing.

        :type name: string
        :param name: The summoner name to search for.

        :type region: string
        :param region: Which game region to search in.

        :returns: A dictionary containing the summoner data.

        Refer to https://www.mashape.com/meepo/league-of-legends#!endpoint-Summoner-ingame-status-and-spectate
        for more information.'''

        name = urllib.quote(name)
        region = self.validate_region(region)

        return self.request('player/%s/%s/ingame' % (region, name))

    def get_summoner_lifetimeip(self, name, region):
        '''Returns the amount of Influence Points a summoner has earned.

        :type name: string
        :param name: The summoner name to search for.

        :type region: string
        :param region: Which game region to search in.

        :returns: A dictionary containing the summoner data.

        Refer to https://www.mashape.com/meepo/league-of-legends#!endpoint-Summoner-lifetime-influence-points
        for more information.'''

        name = urllib.quote(name)
        region = self.validate_region(region)

        return self.request('player/%s/%s/influence_points' % (region, name))

    def get_masteries(self, name, region):
        '''Returns information on each of the summoner's mastery pages.

        :type name: string
        :param name: The summoner name to search for.

        :type region: string
        :param region: Which game region to search in.

        :returns: A dictionary containing the summoner data.

        Refer to https://www.mashape.com/meepo/league-of-legends#!endpoint-Summoner-masteries
        for more information.'''

        name = urllib.quote(name)
        region = self.validate_region(region)

        return self.request('player/%s/%s/mastery' % (region, name))

    def get_current_masteries(self, name, region):
        '''Returns information on the summoner's active mastery page.

        :type name: string
        :param name: The summoner name to search for.

        :type region: string
        :param region: Which game region to search in.

        :returns: A dictionary containing the summoner data.

        Refer to https://www.mashape.com/meepo/league-of-legends#!endpoint-Summoner-masteries
        for more information.'''

        name = urllib.quote(name)
        region = self.validate_region(region)

        return self.request('player/%s/%s/mastery' % (region, name),
                            {'X-Options' : 'SingleEntity'})

    def get_match_history(self, name, region):
        '''Returns date on the last 10 games a summoner has played.

        :type name: string
        :param name: The summoner name to search for.

        :type region: string
        :param region: Which game region to search in.

        :returns: Two dictionaries.

        Refer to https://www.mashape.com/meepo/league-of-legends#!endpoint-Summoner-match-history
        for more information.'''

        name = urllib.quote(name)
        region = self.validate_region(region)

        req = self.request('player/%s/%s/recent_games' % (region, name))

        return req['player'], req['data']

