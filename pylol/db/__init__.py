# encoding: utf-8
from .tables import *

from sqlalchemy import create_engine, MetaData, Table, Column, ForeignKey, \
                       ForeignKeyConstraint, Date, Integer, String, Boolean, \
                       Text
from sqlalchemy.orm import sessionmaker, mapper
from sqlalchemy.exc import NoSuchTableError

def db_connect(uri, init=False):
    '''Connect to the database specified by *uri*.

    :type uri: string
    :param url: A database URI

    :returns: A tuple containing the SQLAlchemy database engine and metadata
        objects.

    Calls the SQLAlchemy methods ``create_engine`` and ``MetaData`` for the
    given URI and returns both objects.'''

    db = create_engine(uri, encoding='utf8')

    meta = TableBase.metadata
    meta.bind = db

    Session = sessionmaker(bind=db)
    session = Session()

    if init:
        db_init(meta)
    else:
        # Load the Pylol table, if its not there chances are this is a fresh DB
        try: pylol = Table('pylol', meta, autoload=True)
        except (NoSuchTableError):
            print 'Cannot load Pylol table, have you run pylol-init?'
            exit(1)

        # Load remaining tables
        summoners = Table('summoners', meta, autoload=True)
        games = Table('games', meta, autoload=True)
        players = Table('players', meta, autoload=True)
        stats = Table('stats', meta, autoload=True)
        champions = Table('champions', meta, autoload=True)

        mapper(Pylol, pylol)
        mapper(Summoner, summoners)
        mapper(Game, games)
        mapper(Player, players)
        mapper(Stat, stats)
        mapper(Champion, champions)

    return (db, meta, session)

def db_init( meta):
    '''Initializes a fresh database'''

    pylol = Table('pylol', meta,
        Column('key', String(30), primary_key=True),
        Column('value', String(30))
    )

    summoners = Table('summoners', meta,
        Column('summonerId', Integer, primary_key=True),
        Column('accountId', Integer, unique=True),
        Column('region', String(3)),
        Column('name', String(30)),
        Column('internalName', String(30)),
        Column('level', Integer),
        Column('icon', Integer)
    )

    games = Table('games', meta,
        Column('gameId', Integer, primary_key=True),
        Column('userId', Integer, ForeignKey('summoners.accountId'),
               primary_key=True),
        Column('region', String(3)),
        Column('adjustedRating', Integer),
        Column('afk', Boolean),
        Column('boostIpEarned', Integer),
        Column('boostXpEarned', Integer),
        Column('championId', Integer),
        Column('createDate', Integer),
        Column('dataVersion', Integer),
        Column('difficulty', Integer),
        Column('difficultyString', String(20)),
        Column('eligibleFirstWinOfDay', Boolean),
        Column('eloChange', Integer),
        Column('experienceEarned', Integer),
        Column('futureData', String(50)),
        Column('gameMapId', Integer),
        Column('gameMode', Integer),
        Column('gameType', Integer),
        Column('gameTypeEnum', Integer),
        Column('id', Integer),
        Column('invalid', Boolean),
        Column('ipEarned', Integer),
        Column('KCoefficient', Integer),
        Column('leaver', Boolean),
        Column('level', Integer),
        Column('predictedWinPct', Integer),
        Column('premadeSize', Integer),
        Column('premadeTeam', Boolean),
        Column('queueType', String(30)),
        Column('ranked', Boolean),
        Column('rating', Integer),
        Column('rawStatsJson', String(50)),
        Column('skinIndex', Integer),
        Column('skinName', String(50)),
        Column('spell1', Integer),
        Column('spell2', Integer),
        Column('subType', String(30)),
        Column('summonerId', Integer),
        Column('teamId', Integer),
        Column('teamRating', Integer),
        Column('timeInQueue', Integer),
        Column('userServerPing', Integer)
    )

    players = Table('players', meta,
        Column('gameId', Integer, primary_key=True),
        Column('summonerId', Integer, primary_key=True),
        Column('championId', Integer),
        Column('teamId', Integer),
        Column('dataVersion', Integer),
        Column('futureData', String(50))
    )

    stats = Table('stats', meta,
        Column('gameId', Integer, primary_key=True),
        Column('userId', Integer, primary_key=True),
        Column('ASSISTS', Integer),
        Column('BARRACKS_KILLED', Integer),
        Column('CHAMPIONS_KILLED', Integer),
        Column('GOLD_EARNED', Integer),
        Column('ITEM0', Integer),
        Column('ITEM1', Integer),
        Column('ITEM2', Integer),
        Column('ITEM3', Integer),
        Column('ITEM4', Integer),
        Column('ITEM5', Integer),
        Column('LARGEST_CRITICAL_STRIKE', Integer),
        Column('LARGEST_KILLING_SPREE', Integer),
        Column('LARGEST_MULTI_KILL', Integer),
        Column('LEVEL', Integer),
        Column('LOSE', Integer),
        Column('MAGIC_DAMAGE_DEALT_PLAYER', Integer),
        Column('MAGIC_DAMAGE_DEALT_TO_CHAMPIONS', Integer),
        Column('MAGIC_DAMAGE_TAKEN', Integer),
        Column('MINIONS_KILLED', Integer),
        Column('NEUTRAL_MINIONS_KILLED', Integer),
        Column('NEUTRAL_MINIONS_KILLED_ENEMY_JUNGLE', Integer),
        Column('NEUTRAL_MINIONS_KILLED_YOUR_JUNGLE', Integer),
        Column('NUM_DEATHS', Integer),
        Column('PHYSICAL_DAMAGE_DEALT_PLAYER', Integer),
        Column('PHYSICAL_DAMAGE_DEALT_TO_CHAMPIONS', Integer),
        Column('PHYSICAL_DAMAGE_TAKEN', Integer),
        Column('SIGHT_WARDS_BOUGHT_IN_GAME', Integer),
        Column('TOTAL_DAMAGE_DEALT', Integer),
        Column('TOTAL_DAMAGE_DEALT_TO_CHAMPIONS', Integer),
        Column('TOTAL_DAMAGE_TAKEN', Integer),
        Column('TOTAL_HEAL', Integer),
        Column('TOTAL_TIME_CROWD_CONTROL_DEALT', Integer),
        Column('TOTAL_TIME_SPENT_DEAD', Integer),
        Column('TRUE_DAMAGE_DEALT_PLAYER', Integer),
        Column('TRUE_DAMAGE_DEALT_TO_CHAMPIONS', Integer),
        Column('TRUE_DAMAGE_TAKEN', Integer),
        Column('TURRETS_KILLED', Integer),
        Column('VISION_WARDS_BOUGHT_IN_GAME', Integer),
        Column('WARD_KILLED', Integer),
        Column('WARD_PLACED', Integer),
        Column('WIN', Integer),

        ForeignKeyConstraint(['gameId', 'userId'],
                             ['games.gameId', 'games.userId'])
    )

    champions = Table('champions', meta,
        Column('key', Integer, primary_key=True),
        Column('name', String(30)),
        Column('version', String(15)),
        Column('id', String(30)),
        Column('title', String(50)),
        Column('blurb', Text),
        Column('attack', Integer),
        Column('defense', Integer),
        Column('magic', Integer),
        Column('difficulty', Integer),
        Column('img_full', String(30)),
        Column('img_sprite', String(30)),
        Column('img_group', String(30)),
        Column('img_x', Integer),
        Column('img_y', Integer),
        Column('img_w', Integer),
        Column('img_h', Integer),
        Column('tags', Text),
        Column('partype', String(30)),
        Column('hp', Integer),
        Column('hpperlevel', Integer),
        Column('mp', Integer),
        Column('mpperlevel', Integer),
        Column('movespeed', Integer),
        Column('armor', Integer),
        Column('armorperlevel', Integer),
        Column('spellblock', Integer),
        Column('spellblockperlevel', Integer),
        Column('attackrange', Integer),
        Column('hpregen', Integer),
        Column('hpregenperlevel', Integer),
        Column('mpregen', Integer),
        Column('mpregenperlevel', Integer),
        Column('crit', Integer),
        Column('critperlevel', Integer),
        Column('attackdamage', Integer),
        Column('attackdamageperlevel', Integer),
        Column('attackspeedoffset', Integer),
        Column('attackspeedperlevel', Integer)
    )

    meta.create_all()

    mapper(Pylol, pylol)
    mapper(Summoner, summoners)
    mapper(Game, games)
    mapper(Player, players)
    mapper(Stat, stats)
    mapper(Champion, champions)
