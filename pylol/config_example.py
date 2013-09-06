# encoding: utf8
'''PyLoL configuration

Once you have filled in your required settings, save and rename this file to
config.py before running Pylol.'''

# Enable/Disable debug mode
debug = False

# URI of the database to use in the form:
#    dbbtype://user:pass@host:port/dbname
# Eg:
#   default_uri = 'mysql://pylol:P@ssw0rd1@db.example.com:3306/pyloldb'
# Leave as None to use local sqlite database
default_uri = None

# Mashape League of Legends API key
# https://www.mashape.com/keys
default_key = ''

# Minimum time in seconds between champion list updates
# Note: if an unknown champion is ever encountered, a champion list update will
# be forced regardless of this value.
champ_upd_wait = 3600*24*14 # 2 weeks

# Minimum time in seconds between item list updates
# Note: if an unknown item is ever encounted, an item list update will be forced
# regardless of this value
item_upd_wait = 3600*24*14 # 2 weeks
