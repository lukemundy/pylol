from setuptools import setup, find_packages

setup(
    name            = 'PyLoL',
    version         = '0.1dev',
    author          = 'Luke Mundy',
    author_email    = 'lmundy@gmail.com',
    url             = 'lmundy.com',
    description     = 'A module for accessing data from the Elophant API',
    packages        = find_packages(),
    package_data    = { 'pylol': ['data/*.sqlite'] },

    install_requires = [
        'SQLAlchemy>=0.8',
        'simplejson>=2.2.1',
        'pytz',
        'python-dateutil'
    ],

    entry_points = {
        'console_scripts': [
            'pylol-init = pylol.main:init',
            'pylol-update = pylol.main:update',
            'pylol-report = pylol.main:report'
        ],
    },
)

