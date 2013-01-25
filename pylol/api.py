# encoding: utf8
import urllib2
import simplejson as json

from .exceptions import APIFailure, InvalidRegion

class Api(object):
    '''Object for accessing data from api.elophant.com'''

    _url = u'http://api.elophant.com/v2/'
    _regions = (u'na', u'euw', u'eune', u'br')

    def __init__(self, key):
        '''Class constructor

        Arguments:
        key -- Elophant access key (get a key elophant.com/developers/new)
        '''

        self.key = key

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

        data = json.loads(urllib2.urlopen(url).read())

        if not data['success']:
            raise APIFailure(data['error'])
        else:
            return data['data']
