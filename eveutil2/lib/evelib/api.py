# EVE API library

import base64
import hashlib
import os
import time

import evelib.eveapi as eveapi
import evelib.config as config

# Fix eveapi warnings
import warnings, re
warnings.filterwarnings("ignore",
                        "BaseException.message has been deprecated")

_keylist = None
def keylist(configfile=None):
    if configfile is None:
        configfile = config.get("api", "keyfile")
    global _keylist
    if _keylist is None:
        _keylist = []
        f = file(configfile)
        for line in f.readlines():
            line = line.strip()
            (userid, apikey, charid, charname) = line.split(":")
            _keylist.append((userid, apikey, charid, charname))
    return _keylist

def key(name=None, configfile=None):
    for (userid, apikey, charid, charname) in keylist(configfile):
        if name is None or charname == name:
            return (userid, apikey, charid)

def api():
    cachedir = config.get("api", "cache")
    if cachedir is None:
        return eveapi.EVEAPIConnection()
    else:
        return eveapi.EVEAPIConnection(cacheHandler=FileCache(cachedir))

def account(name=None, configfile=None):
    (userid, apikey, charid) = key(name, configfile)
    return api().auth(userID=userid, apiKey=apikey)

def character(name=None, configfile=None):
    (userid, apikey, charid) = key(name, configfile)
    return account(name, configfile).character(characterID=charid)

def corp(name=None, configfile=None):
    (userid, apikey, charid) = key(name, configfile)
    char = character(name, configfile)
    char.context()._path = "/corp"
    return char

class FileCache(object):
    def __init__(self, dir):
        self.dir = dir

    def retrieve(self, host, path, params):
        fname = self.get_file_name(host, path, params)
        try:
            f = file(fname)
        except Exception:
            return None
        cached_until = int(f.readline())
        if time.time() > cached_until:
            os.unlink(fname)
            return None
        else:
            return f

    def store(self, host, path, params, doc, obj):
        f = file(self.get_file_name(host, path, params), "w")
        if hasattr(obj, 'cachedUntil'):
            f.write("%i\n" % obj.cachedUntil)
        else:
            f.write("%i\n" % obj.result.cachedUntil)
        f.write(doc)
        f.close()

    def get_file_name(self, host, path, params):
        p = params.items()
        p.sort()
        pstring = "&".join(["%s=%s" % (base64.b64encode(str(a)),
                                       base64.b64encode(str(b)))
                            for (a, b) in p])
        fname = hashlib.md5("%s&%s&%s" % (base64.b64encode(host),
                                          base64.b64encode(path),
                                          base64.b64encode(pstring))).hexdigest()
        return os.path.join(self.dir, fname)
