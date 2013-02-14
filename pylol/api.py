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

        :returns: A dictionary containing the decoded JSON data.

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
        '''Returns data on each item.

        :returns: A list of dictionaries.

        Refer to http://elophant.com/developers/docs/items for more
        information.'''

        return self.request('items')

    def get_champions(self):
        '''Returns a mapping of champion IDs to names.

        :returns: A list of dictionaries.

        Refer to http://elophant.com/developers/docs/champions for more
        information'''

        return self.request('champions')

    def get_summoner(self, name, region = None):
        '''Returns some basic information on a summoner.

        :type name: string
        :param name: The summoner name to search for.

        :type region: string
        :param region: Which game region to search in.

        :returns: A dictionary containing the summoner data.

        Refer to http://elophant.com/developers/docs/summoner for more
        information.

        .. NOTE::
            The ``revisionDate`` field returned from the API will be converted
            into a proper unix timestamp.'''

        path = u'summoner/%s' % urllib.quote(name)

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
        '''Returns each of a Summoner's current mastery pages.

        :type sid: int
        :param sid: The summoner's ``summonerId``.

        :type region: string
        :param region: Which game region to search in.

        :returns: A dictionary containing info on the mastery pages.

        Refer to http://elophant.com/developers/docs/mastery_pages for more
        information.'''

        path = u'mastery_pages/%d' % sid

        return self.request(path, region)

    def get_rune_pages(self, sid, region = None):
        '''Returns each of a Summoner's current rune pages.

        :type sid: int
        :param sid: The summoner's ``summonerId``.

        :type region: string
        :param region: Which game region to search in.

        :returns: A dictionary containing info on the rune pages.

        Refer to http://elophant.com/developers/docs/rune_pages for more
        information.'''

        path = u'rune_pages/%d' % sid

        return self.request(path, region)

    def get_recent_games(self, aid, region = None):
        '''Returns information and game stats from up to 10 of the Summoner's
        most recent games.

        :type aid: int
        :param aid: The summoner's ``accountId``.

        :type region: string
        :param region: Which game region to search in.

        :returns: A dictionary containing the game data.

        If there are no recent games played by the summoner, an empty
        dictionary will be returned instead.

        .. WARNING::
            Make sure that *aid* contains the ``accountId`` of the summoner and
            not their ``summonerId`` that is used by most other Api functions.

        .. NOTE::
            The ``createDate`` field in each game's ``gameStatistics`` will be
            converted into a proper unix timestamp.

        Refer to http://elophant.com/developers/docs/recent_games for more
        information.'''

        path = u'recent_games/%d' % aid

        try:
            ret = self.request(path, region)
        except APIFailure as e:
            if re.search(r'^No recent games were found for accountId [0-9]+\.',
                         e.message):
                ret = dict()
            else:
                raise
        else:
            # Convert createDate into a proper unix timestamp
            for k, g in enumerate(ret['gameStatistics']):
                ts = int(re.sub(r'[^0-9]+', '', g['createDate']))
                ret['gameStatistics'][k]['createDate'] = ts / 1000.0

        return ret

    def get_summoner_names(self, sids, region = None):
        '''Maps the supplied summoner IDs to their associated summoner names.

        :type sids: list
        :param sids: A list of summoner IDs.

        :type region: string
        :param region: Which game region to search in.

        :returns: A list containing the summoner names in the same order the
            summoner IDs were provided.

        Refer to http://elophant.com/developers/docs/summoner_names for more
        information.'''

        if type(sids) is not list:
            raise TypeError('get_summoner_names() - Expected a list but was '
                            'passed a value of type "%s" instead.'
                            % type(sids).__name__)

        path = u'summoner_names/%d' % ','.join(sids)

        return self.request(path, region)

    def get_leagues(self, sid, region = None):
        '''Returns information on each league the summoner is currently in.

        :type sid: int
        :param sid: The summoner's ``summonerId``.

        :type region: string
        :param region: Which game region to search in.

        :returns: A list of dictionaries containing info on each league.

        Refer to http://elophant.com/developers/docs/leagues for more
        information.'''

        path = u'leagues/%d' % ','.join(sids)

        return self.request(path, region)

    def get_ranked_stats(self, aid, season = 'current', region = None):
        '''Returns all ranked stats for the specified summoner and season.

        :type aid: int
        :param aid: The summoner's ``accountId``.

        :type season: string
        :param season: Which season to get stats for.

        :type region: string
        :param region: Which game region to search in.

        :returns: A dictionary containing the stats.

        .. WARNING::
            Make sure that *aid* contains the ``accountId`` of the summoner and
            not their ``summonerId`` that is used by most other Api functions.

        The optional parameter *season* should be one of ``'one'``, ``'two'``
        or ``'current'`` (the default).

        Refer to http://elophant.com/developers/docs/ranked_stats for more
        information.'''

        if season not in ('one', 'two', 'current'):
            raise ValueError('get_ranked_stats() - season should be one of '
                             '"one", "two" or "current". Received "%s" '
                             'instead.' % season)

        path = u'ranked_stats/%d/%s' % (aid, season)

        ret = self.request(path, region)

    def get_summoner_team_info(self, sid, region = None):
        '''Returns information on each team the summoner is currently in.

        :type sid: int
        :param sid: The summoner's ``summonerId``.

        :type region: string
        :param region: Which game region to search in.

        :returns: A dictionary containing the team information.

        If the summoner is not a member of any teams, an empty dictionary will
        be returned instead.

        Refer to http://elophant.com/developers/docs/summoner_team_info for
        more information.'''

        path = u'summoner_team_info/%d' % sid

        try:
            ret = self.request(path, region)
        except APIFailure as e:
            if re.search(r'^No teams found for summoner [0-9]+\.$', e.message):
                ret = dict()
            elif re.search(r'^No summoner found with summonerId [0-9]+\.$',
                           e.message):
                raise APISummonerIDNotFound(sid, region)
            else:
                raise

        return ret

    def get_in_progress_game_info(self, name, region = None):
        '''Returns player info, picks, bans and observer info for the game
        the specified summoner is currently in (if any).

        :type name: string
        :param name: The summoner name to search for.

        :type region: string
        :param region: Which game region to search in.

        :returns: A dictionary containing the game information.

        If the summoner is not currently in a game, an empty dictionary will
        be returned instead.

        Refer to http://elophant.com/developers/docs/in_progress_game_info for
        more information.'''

        path = u'in_progress_game_info/%s' % name

        try:
            ret = self.request(path, region)
        except APIFailure as e:
            if re.search(r'^Summoner .+ was not found in the system!$',
                         e.message):
                raise APISummonerNotFound(name, region)
            elif re.search(r'^No Game for player .+ was found in the\
            system!$', e.message):
                ret = dict()
            else:
                raise

        return ret

    def get_team(self, tid, region = None):
        '''Returns information on the requested team.

        :type tid: string
        :param tid: The team's ``teamId``.

        :type region: string
        :param region: Which game region to search in.

        :returns: A dictionary containing all info on the requested team.

        Refer to http://elophant.com/developers/docs/team for more
        information.'''

        path = u'team/%s' % tid

        return self.request(path, region)

    def get_find_team(self, name, region = None):
        '''Funtionally identical to get_team() but will search on team name or
        tag instead of ID.

        :type name: string
        :param name: A team's tag or name.

        :type region: string
        :param region: Which game region to search in.

        :returns: If a matching team is found, a dictionary containing all info
            on the requested team.

        Elophant asks that this method be used sparingly and only if the
        ``teamId`` of a team is not known.

        Refer to http://elophant.com/developers/docs/find_team for more
        information.'''

        path = u'find_team/%s' % urlib.quote(name)

        return self.request(path, region)


    def get_team_end_of_game_stats(self, tid, gid, region = None):
        '''Returns very detailed statistics about the requested ranked match.

        :type tid: string
        :param tid: The team's ``teamId``.

        :type gid: int
        :param gid: The ``gameId`` to look up.

        :type region: string
        :param region: Which game region to search in.

        :returns: A dictionary containing the match statistics.

        Refer to http://elophant.com/developers/docs/team_end_of_game_stats for
        more information.'''

        path = u'team/%s/end_of_game_stats/%d' % (tid, gid)

        return self.request(path, region)

    def get_team_ranked_stats(self, tid, region = None):
        '''Returns stats of each player in the specified team.

        :type tid: string
        :param tid: The team's ``teamId``.

        :type region: string
        :param region: Which game region to search in.

        :returns: A dictionary containing the stats for each team member.

        Refer to http://elophant.com/developers/docs/team_ranked_stats for
        more information.'''

        path = u'team/%s/ranked_stats' % tid

        return self.request(path, region)
