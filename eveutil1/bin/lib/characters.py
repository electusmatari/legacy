# Library to manage EVE characters

import sys
from os import path

import eveapi

import warnings, re
warnings.filterwarnings("ignore",
                        "BaseException.message has been deprecated")

configfile = path.expanduser("~/.evecharacters")

def list(configfile=configfile):
    f = file(configfile)
    chars = {}
    for line in f.readlines():
        line = line.strip()
        (userid, apikey, charid, name) = line.split(":")
        chars[name] = (userid, apikey, charid)
    f.close()
    return chars

def default(configfile=configfile):
    f = file(configfile)
    (userid, apikey, charid, name) = f.readline().strip().split(":")
    return (name, userid, apikey, charid)

def api(cacheHandler=None):
    return eveapi.EVEAPIConnection(cacheHandler=cacheHandler)

def auth(name=None, cacheHandler=None, configfile=configfile):
    if name is None:
        (name, userid, apikey, charid) = default(configfile)
    else:
        chars = list(configfile)
        (userid, apikey, charid) = chars[name]
    return eveapi.EVEAPIConnection(cacheHandler=cacheHandler).auth(userID=userid, apiKey=apikey)

def char(name=None, cacheHandler=None, configfile=configfile):
    if name is None:
        (name, userid, apikey, charid) = default(configfile)
    else:
        chars = list(configfile)
        (userid, apikey, charid) = chars[name]
    return eveapi.EVEAPIConnection(cacheHandler=cacheHandler).auth(userID=userid, apiKey=apikey).character(characterID=charid)

def corp(name=None, cacheHandler=None, configfile=configfile):
    character = char(name=name, cacheHandler=cacheHandler,
                     configfile=configfile)
    context = character.context()
    context._path = "/corp"
    return character
