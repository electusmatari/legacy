import ConfigParser
import os

conf = ConfigParser.SafeConfigParser()
conf.read([os.path.expanduser("~/.eve.cfg")])

def get(section, option, default=None):
    if conf.has_option(section, option):
        return conf.get(section, option)
    else:
        return default
