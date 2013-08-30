# encoding: utf-8
from sqlalchemy.ext.declarative import declarative_base

TableBase = declarative_base()

class Pylol(object):
    '''A table of key/value pairs holding various setting and variables needed
    between instances of Pylol'''

    __tablename__ = 'pylol'

    def __init__(self, key, value):
        self.key = key
        self.value = value

class PylolBase(object):
    '''Base table object that all other tables will inherit'''

    def __init__(self, **data):
        '''Allows creation of a new row by simply supplying a dictionary with
        the relevant key:value pairs'''

        self.update_values(**data)

    def update_values(self, **data):
        '''Allows simple updating of a row by supplying a dictionary with the
        relevant key:value pairs that need updating'''

        self.__dict__.update(data)

class Summoner(PylolBase):
    '''Information on a particular summoner'''
    __tablename__ = 'summoners'
    __singlename__ = 'summoner'

    def __init__(self, region, **data):
        self.region = region
        super(Summoner, self).update_values(**data)

class Game(PylolBase):
    '''An instance of a game from the point of view of a player'''
    __tablename__ = 'games'
    __singlename__ = 'game'

    def __init__(self, region, **data):
        self.region = region
        super(Game, self).update_values(**data)

class Player(PylolBase):
    '''Ties a summoner to a specific game'''
    __tablename__ = 'players'
    __singlename__ = 'player'


class Stat(PylolBase):
    '''Contains player statistics for a specific game'''
    __tablename__ = 'stats'
    __singlename__ = 'stat'

    def __init__(self, gameId, userId, data):
        self.gameId = gameId
        self.userId = userId
        for s in data: setattr(self, s['statType'], s['value'])

class Champion(PylolBase):
    '''Champion information'''
    __tablename__ = 'champions'
    __singlename__ = 'champion'

    def __init__(self, data):
        self.version = data['version']
        self.id = data['id']
        self.key = data['key']
        self.name = data['name']
        self.title = data['title']
        self.blurb = data['blurb']
        self.partype = data['partype']
        self.tags = ','.join(data['tags'])

        self.update_values(**data['info'])
        self.update_values(**data['stats'])

        for key, value in data['image'].iteritems():
            setattr(self, 'img_%s' % key, value)
