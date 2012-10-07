import os

import ConfigParser

conf = None

def get():
    global conf
    if conf is None:
        conf = ConfigParser.SafeConfigParser()
        conf.optionxform = str
        conf.read([os.path.expanduser("~/.eve.cfg")])
    return conf
