# encoding: utf8
import urllib2
import re
import simplejson as json

from .exceptions import APIFailure, APIInvalidRegion

class Api(object):
    '''A wrapper class for pulling data from the `Elophant API
    <http://elophant.com/developers/docs>`_.'''

    # Public vars
    key          = u''  # Elophant API key
    num_requests = 0    # How many API requests have been made

    # Private vars
    _url     = u'http://api.elophant.com/v2/'  # Full URL to the API
    _regions = (u'na', u'euw', u'eune', u'br') # API region names

    def __init__(self, key):
        '''
        :type key: string
        :param key: API developer key.

        If you do not yet have a developer key to access the API you can
        request a new one from http://elophant.com/developers/new.'''

        self.key = unicode(key)

    def request(self, path, region = None):
        '''Send a request to the Elophant API.

        :type path: string
        :param path: Path to the desired API resource.

        :type region: string
        :param region: Which game region to query.

        :returns: A dict containing the decoded JSON returned from the API.

        Makes an API request to the given path and returns the decoded JSON as
        a dictionary.

        *path* will have any leading or trailing slash stripped before the
        request is made, so you should not include them if you can avoid it.

        *region* should be one of ``NA`` for North America, ``EUW`` for Europe
        West, ``EUNE`` for Europe North East and ``BR`` for Brazil. If *region*
        is omitted or ``None`` is supplied it will default to ``NA``. Upper or
        lower case strings can be passed as *path* is not case-sensitive.'''

        if region is not None:
            region = unicode(region).lower()

            if region not in self._regions:
                raise APIInvalidRegion(region)
        else:
            region = self._regions[0]

        # Remove slashes from start/end of path
        if path[0] is '/': path = path[1:]
        if path[-1] is '/': path = path[:-1]

        if 'items' in path or 'champions' in path:
            url = u'%s%s?key=%s' % (self._url, path, self.key)
        else:
            url = u'%s%s/%s?key=%s' % (self._url, region, path, self.key)

        # Make the request
        try:
            data = json.loads(urllib2.urlopen(url).read())
        except json.JSONDecodeError as e:
            raise APIInvalidData(e.doc)

        self.num_requests += 1;

        if not data['success']:
            raise APIFailure(data['error'], path, url)
        else:
            return data['data']

    def get_items(self):
        '''Returns data on all in game items'''

        return self.request('items')

    def get_champions(self):
        '''Returns the name and ID of all champions'''

        return self.request('champions')

    def get_summoner(self, name, region = None):
        '''Returns name, icon, ID and level of the specified summoner

        Arguments:
        name -- Display name of the summoner to look for.
        region -- Which region to search in.
        '''

        path = 'summoner/%s' % urllib.quote(name)

        try:
            ret = self.request(path, region)
        except APIFailure as e:
            if re.search(r'^Summoner .+ was not found.$', e.message):
                raise APISummonerNotFound(name, region)
            else:
                raise

        # Convert revisionDate into a proper unix timestamp
        ret['revisionDate'] = int(re.sub(r'[^0-9]+', '', ret['revisionDate']))
        ret['revisionDate'] /= 1000.0

        return ret

    def get_mastery_pages(self, sid, region = None):
        '''Returns all of a Summoner's mastery pages

        Arguments:
        sid -- ID of the summoner to look up (returned from get_summoner()).
        region -- Which region to search in.
        '''

        path = 'mastery_pages/%d' % sid

        return self.request(path, region)

    def get_rune_pages(self, sid, region = None):
        '''Returns all of a Summoner's rune pages

        Arguments:
        sid -- ID of the summoner to look up (returned from get_summoner()).
        region -- Which region to search in.
        '''

        path = 'rune_pages/%d' % sid

        return self.request(path, region)

    def get_recent_games(self, aid, region = None):
        '''Returns all information and stats from a Summoner's last 10 games

        Arguments:
        aid -- Account ID (not summoner ID) of the summoner to look up.
        region -- Which region to search in.
        '''

        path = 'recent_games/%d' % aid

        ret = self.request(path, region)

        # Convert createDate into a proper unix timestamp
        for k, g in enumerate(ret['gameStatistics']):
            ts = float(re.sub(r'[^0-9]+', '', g['createDate']))
            ret['gameStatistics'][k]['createDate'] = ts / 1000

        return ret

    def get_summoner_names(self, sids, region = None):
        '''Returns the names of each summoner

        Arguments:
        sids -- A list of summoner IDs to look up.
        region -- Which region to search in.
        '''

        path = 'summoner_names/%d' % ','.join(sids)

        return self.request(path, region)

    def get_leagues(self, sid, region = None):
        '''Returns information on each league the summoner is currently in

        Arguments:
        sid -- ID of the summoner to look up.
        region -- Which region to search in.
        '''

        path = 'leagues/%d' % ','.join(sids)

        return self.request(path, region)

    def get_ranked_stats(self, aid, season = None, region = None):
        '''Returns all information and stats from a Summoner's last 10 games

        Arguments:
        aid -- Account ID (not summoner ID) of the summoner to look up.
        season -- Which season to get stats for ('one', 'two' or 'current')
        region -- Which region to search in.
        '''

        if season is not None:
            path = 'ranked_stats/%d/%s' % (aid, season)
        else:
            path = 'ranked_stats/%d' % aid

        ret = self.request(path, region)

    def get_summoner_team_info(self, sid, region = None):
        '''Returns information on each team the summoner is currently in

        Arguments:
        sid -- ID of the summoner to look up.
        region -- Which region to search in.
        '''

        path = 'summoner_team_info/%d' % sid

        try:
            ret = self.request(path, region)
        except APIFailure as e:
            if re.search(r'^No teams found for summoner [0-9]+\.$', e.message):
                raise APISummonerNotInTeams(sid, region)
            elif re.search(r'^No summoner found with summonerId [0-9]+\.$',
                              e.message):
                raise APISummonerIDNotFound(sid, region)
            else:
                raise

        return ret

    def get_in_progress_game_info(self, name, region = None):
        '''Returns player info, picks, bans and observer info for the game
        the specified summoner is currently in (if any).

        Arguments:
        name -- Name of the summoner to look up.
        region -- Which region to search in.
        '''

        path = 'in_progress_game_info/%s' % name

        try:
            ret = self.request(path, region)
        except APIFailure as e:
            if re.search(r'^Summoner .+ was not found in the system!$',
                         e.message):
                raise APISummonerNotFound(name, region)
            elif re.search(r'^No Game for player .+ was found in the\
            system!$', e.message):
                raise APISummonerNotFound(name, region)
            else:
                raise

        return ret

    def get_team(self, tid, region = None):
        '''Returns information on the requested team

        Arguments:
        tid -- teamId of the team to look up.
        region -- Which region to search in.
        '''

        path = 'team/%s' % tid

        return self.request(path, region)

    def get_find_team(self, name, region = None):
        '''Returns information on the requested team

        Arguments:
        name -- Name or tag of the team to search for.
        region -- Which region to search in.
        '''

        path = 'find_team/%s' % urlib.quote(name)

        return self.request(path, region)


    def get_team_end_of_game_stats(self, tid, gid, region = None):
        '''Returns detailed statistics about the requested ranked match

        Arguments:
        tid -- Team ID of the team to return stats for.
        gid -- ID of the game to return stats for.
        region -- Which region to search in.
        '''

        path = 'team/%s/end_of_game_stats/%d' % (tid, gid)

        return self.request(path, region)

    def get_team_end_of_game_stats(self, tid, region = None):
        '''Returns stats of each player in the specified team

        Arguments:
        tid -- Team ID of the team to return stats for.
        region -- Which region to search in.
        '''

        path = 'team/%s/ranked_stats' % tid

        return self.request(path, region)
