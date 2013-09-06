# coding: utf8
'''Pylol Database Schema'''

from sqlalchemy import MetaData, Column, ForeignKey, ForeignKeyConstraint
from sqlalchemy.types import *
from sqlalchemy.ext.declarative import declarative_base

metadata = MetaData()

class Base(object):
    '''Base class that all declarative tables will inherit from.'''

    def __init__(self, data):
        '''Allows neat creation of table objects.

        :type data: dict
        :param data: A dictionary of key/value pairs.

        Since many of our tables have a large number of columns and since API
        calls return dictionaries, being able to pass a dictionary with data
        for the table saves a bunch of time and avoids giant parameter lists.'''

        self.update_values(data)

    def update_values(self, data):
        '''Takes a dictionary and updates class members.

        :type data: dict
        :param data: A dictionary of key/value pairs.'''

        for key, val in data.items():
            setattr(self, key, val)

Base = declarative_base(metadata=metadata, cls=Base)

class Registry(Base):
    '''A variable and associated value used by Pylol.'''

    __tablename__ = 'registry'

    def __init__(self, key, value):
        '''Create a new registry key/value.

        :type key: string
        :param key: Name of the key

        :type value: mixed
        :param value: Key value

        Since there are only two columns in this table there is no need to use
        the inherited constructor to update via a dict.'''

        self.key = key
        self.value = value

    key = Column(String(30), primary_key=True)
    value = Column(String(30))

class Summoner(Base):
    '''A user's Summoner account.

    :type region: string
    :param region: The region this summoner is from.'''

    __tablename__ = 'summoners'

    def __init__(self, region, data):
        self.region = region
        self.update_values(data)

    summonerId = Column(Integer, primary_key=True)
    accountId = Column(Integer, unique=True)
    region = Column(String(3))
    name = Column(String(30), index=True)
    internalName = Column(String(30))
    level = Column(Integer)
    icon = Column(Integer)
    lastUpdate = Column(Integer)

class Game(Base):
    '''A single game played by a summoner.

    :type region: string
    :param region: The region this game was played on.'''

    __tablename__ = 'games'

    def __init__(self, region, data):
        self.region = region
        self.update_values(data)

    gameId = Column(Integer, primary_key=True)
    userId = Column(Integer, ForeignKey('summoners.accountId'),primary_key=True)
    region = Column(String(3))
    adjustedRating = Column(Integer)
    afk = Column(Boolean)
    boostIpEarned = Column(Integer)
    boostXpEarned = Column(Integer)
    championId = Column(Integer, ForeignKey('champions.key'))
    createDate = Column(Integer)
    dataVersion = Column(Integer)
    difficulty = Column(Integer)
    difficultyString = Column(String(20))
    eligibleFirstWinOfDay = Column(Boolean)
    eloChange = Column(Integer)
    experienceEarned = Column(Integer)
    futureData = Column(String(50))
    gameMapId = Column(Integer)
    gameMode = Column(String(30))
    gameType = Column(String(30))
    gameTypeEnum = Column(String(30))
    id = Column(String(20))
    invalid = Column(Boolean)
    ipEarned = Column(Integer)
    KCoefficient = Column(Integer)
    leaver = Column(Boolean)
    level = Column(Integer)
    predictedWinPct = Column(Integer)
    premadeSize = Column(Integer)
    premadeTeam = Column(Boolean)
    queueType = Column(String(30))
    ranked = Column(Boolean)
    rating = Column(Integer)
    rawStatsJson = Column(String(50))
    skinIndex = Column(Integer)
    skinName = Column(String(50))
    spell1 = Column(Integer)
    spell2 = Column(Integer)
    subType = Column(String(30))
    summonerId = Column(Integer)
    teamId = Column(Integer)
    teamRating = Column(Integer)
    timeInQueue = Column(Integer)
    userServerPing = Column(Integer)

class Stat(Base):
    '''Contains player statistics for a specific game.'''

    __tablename__ = 'stats'

    def __init__(self, gameId, userId, data):
        self.gameId = gameId
        self.userId = userId

        for s in data: setattr(self, s['statType'], s['value'])

        self.WIN = bool(self.WIN)
        self.LOSE = bool(self.LOSE)

    gameId = Column(Integer, primary_key=True)
    userId = Column(Integer, primary_key=True)
    dataVersion = Column(Integer)
    ASSISTS = Column(Integer)
    BARRACKS_KILLED = Column(Integer)
    CHAMPIONS_KILLED = Column(Integer)
    GOLD_EARNED = Column(Integer)
    ITEM0 = Column(Integer)
    ITEM1 = Column(Integer)
    ITEM2 = Column(Integer)
    ITEM3 = Column(Integer)
    ITEM4 = Column(Integer)
    ITEM5 = Column(Integer)
    LARGEST_CRITICAL_STRIKE = Column(Integer)
    LARGEST_KILLING_SPREE = Column(Integer)
    LARGEST_MULTI_KILL = Column(Integer)
    LEVEL = Column(Integer)
    LOSE = Column(Boolean)
    MAGIC_DAMAGE_DEALT_PLAYER = Column(Integer)
    MAGIC_DAMAGE_DEALT_TO_CHAMPIONS = Column(Integer)
    MAGIC_DAMAGE_TAKEN = Column(Integer)
    MINIONS_KILLED = Column(Integer)
    NEUTRAL_MINIONS_KILLED = Column(Integer)
    NEUTRAL_MINIONS_KILLED_ENEMY_JUNGLE = Column(Integer)
    NEUTRAL_MINIONS_KILLED_YOUR_JUNGLE = Column(Integer)
    NUM_DEATHS = Column(Integer)
    PHYSICAL_DAMAGE_DEALT_PLAYER = Column(Integer)
    PHYSICAL_DAMAGE_DEALT_TO_CHAMPIONS = Column(Integer)
    PHYSICAL_DAMAGE_TAKEN = Column(Integer)
    SIGHT_WARDS_BOUGHT_IN_GAME = Column(Integer)
    TOTAL_DAMAGE_DEALT = Column(Integer)
    TOTAL_DAMAGE_DEALT_TO_CHAMPIONS = Column(Integer)
    TOTAL_DAMAGE_TAKEN = Column(Integer)
    TOTAL_HEAL = Column(Integer)
    TOTAL_TIME_CROWD_CONTROL_DEALT = Column(Integer)
    TOTAL_TIME_SPENT_DEAD = Column(Integer)
    TRUE_DAMAGE_DEALT_PLAYER = Column(Integer)
    TRUE_DAMAGE_DEALT_TO_CHAMPIONS = Column(Integer)
    TRUE_DAMAGE_TAKEN = Column(Integer)
    TURRETS_KILLED = Column(Integer)
    VISION_WARDS_BOUGHT_IN_GAME = Column(Integer)
    WARD_KILLED = Column(Integer)
    WARD_PLACED = Column(Integer)
    WIN = Column(Boolean)

    __table_args__ = (
        ForeignKeyConstraint(['gameId', 'userId'],
                             ['games.gameId', 'games.userId']),
        {},
    )

class Champion(Base):
    '''A playable champion.'''

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

        self.update_values(data['info'])
        self.update_values(data['stats'])

        for key, value in data['image'].iteritems():
            setattr(self, 'img_%s' % key, value)

    key = Column(Integer, primary_key=True)
    name = Column(String(30))
    version = Column(String(15))
    id = Column(String(30))
    title = Column(String(50))
    blurb = Column(Text)
    attack = Column(Integer)
    defense = Column(Integer)
    magic = Column(Integer)
    difficulty = Column(Integer)
    img_full = Column(String(30))
    img_sprite = Column(String(30))
    img_group = Column(String(30))
    img_x = Column(Integer)
    img_y = Column(Integer)
    img_w = Column(Integer)
    img_h = Column(Integer)
    tags = Column(Text)
    partype = Column(String(30))
    hp = Column(Integer)
    hpperlevel = Column(Integer)
    mp = Column(Integer)
    mpperlevel = Column(Integer)
    movespeed = Column(Integer)
    armor = Column(Integer)
    armorperlevel = Column(Integer)
    spellblock = Column(Integer)
    spellblockperlevel = Column(Integer)
    attackrange = Column(Integer)
    hpregen = Column(Integer)
    hpregenperlevel = Column(Integer)
    mpregen = Column(Integer)
    mpregenperlevel = Column(Integer)
    crit = Column(Integer)
    critperlevel = Column(Integer)
    attackdamage = Column(Integer)
    attackdamageperlevel = Column(Integer)
    attackspeedoffset = Column(Integer)
    attackspeedperlevel = Column(Integer)

class Player(Base):
    '''Maps a summoner to a game.'''

    __tablename__ = 'players'

    def __init__(self, gameId, data):
        self.gameId = gameId
        self.update_values(data)

    gameId = Column(Integer, primary_key=True)
    summonerId = Column(Integer, primary_key=True)
    championId = Column(Integer)
    teamId = Column(Integer)
    dataVersion = Column(Integer)
    futureData = Column(String(50))

class Group(Base):
    '''A group of summoners.'''

    __tablename__ = 'groups'

    id = Column(Integer, primary_key=True)
    internalName = Column(String(30))
    name = Column(String(30))

class GroupMem(Base):
    '''Maps a summoner to a group.'''

    __tablename__ = 'group_mem'

    groupId = Column(Integer, ForeignKey('groups.id'), primary_key=True)
    summonerId = Column(Integer, ForeignKey('summoners.summonerId'),
                        primary_key=True)

