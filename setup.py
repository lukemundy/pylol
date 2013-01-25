from setuptools import setup, find_packages

setup(
    name            = 'PyLoL',
    version         = '0.1dev',
    author          = 'Luke Mundy',
    author_email    = 'lmundy@gmail.com',
    url             = 'lmundy.com',
    description     = 'A module for accessing data from the Elophant API',
    packages        = find_packages(),

    install_requires = [
        'SQLAlchemy>=0.7',
        'simplejson>=2.2.1'
    ],

    entry_points = {
        'console_scripts': [
            'pylol = pylol.main:main',
        ],
    },
)

