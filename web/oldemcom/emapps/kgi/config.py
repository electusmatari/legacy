import ConfigParser
import os

cfg = None

def config():
    global cfg
    if cfg is None:
        cfg = ConfigParser.ConfigParser()
        cfg.read(['/home/forcer/Projects/private/kgi.cfg'])
    return cfg
