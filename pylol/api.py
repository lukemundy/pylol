# encoding: utf8
import urllib2
import re
import simplejson as json

from .exceptions import APIFailure, InvalidRegion

class Api(object):
    '''Object for accessing data from api.elophant.com'''

    # Public vars
    key          = u''  # Elophant API key
    num_requests = 0    # How many API requests have been made

    # Private vars
    _url     = u'http://api.elophant.com/v2/'  # Full URL to the API
    _regions = (u'na', u'euw', u'eune', u'br') # API region names

    def __init__(self, key):
        '''Class constructor

        Arguments:
        key -- Elophant access key (get a key elophant.com/developers/new)
        '''

        self.key = unicode(key)

    def request(self, path, region = None):
        '''Makes a request to the API

        Arguments:
        path -- Path to the desired API resource
        region -- Which region to query
        '''

        if region not None:
            region = unicode(region).lower()

            if region not in self._regions:
                raise InvalidRegion(region)
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
        '''Returns name, icon, ID and level of the specified summoner'''

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
        '''Returns all of a Summoner's mastery pages'''

        path = 'mastery_pages/%d' % sid

        return self.request(path, region)
