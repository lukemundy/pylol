# coding: utf8
'''Pylol Database'''

from .. import config
from .tables import metadata

from pkg_resources import resource_filename
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def db_connect(uri=None):
    '''Connect to the supplied database URI.

    :type uri: string
    :param uri: An SQLAlchemy database URI.

    :type engine_args: dict

    :returns: An engine and connection object.

    If no URI is supplied, the default SQLite database from the Pylol package
    directory will be used.'''

    if uri is None:
        uri = 'sqlite:///%s' % resource_filename('pylol','data/database.sqlite')

    # We need to explicity set the connection charset for MySQL otherwise it
    # defaults to latin1 - even if the database is in utf8
    if uri.startswith('mysql:'):
        if 'charset' not in uri:
            uri += '?charset=utf8'

    engine = create_engine(uri, convert_unicode=True, echo=config.debug)
    metadata.bind = engine

    Session = sessionmaker(bind=engine)
    session = Session()

    return engine, session
