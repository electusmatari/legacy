import datetime
import os

from reverence.blue import marshal

TRANQUILITY = "87.237.38.200"
CACHEPATHS = [
    "%USERPROFILE%/Local Settings/Application Data/CCP/EVE/",
    "%USERPROFILE%/Lokale Einstellungen/Anwendungsdaten/CCP/EVE/",
    "%USERPROFILE%/Local Settings/Application Data/CCP/EVE/",
    "%LOCALAPPDATA%/CCP/EVE/",
    "%LOCALAPPDATA%/CCP/EVE/"
    ]

def cache_load(filename):
    return marshal.Load(open(filename, "rb").read())

def make_methodcall(meth, with_args=True):
    if type(meth) != tuple:
        return str(meth)
    elif len(meth) == 0:
        return str(meth)
    elif len(meth) == 1:
        return str(meth[0])
    elif with_args:
        return "%s.%s(%s)" % (meth[0], meth[1],
                              ", ".join(str(x) for x in meth[2:]))
    else:
        return "%s.%s" % (meth[0], meth[1])


def find_cache_directories():
    result = []
    for macho in find_cache_machodirs():
        protocol = max(int(name) for name in os.listdir(macho)
                       if name.isdigit())
        methoddir = os.path.join(macho, str(protocol), "CachedMethodCalls")
        if os.path.isdir(methoddir):
            result.append(os.path.normpath(methoddir))
    return result


def find_cache_machodirs():
    basedir = find_cache_basedir()
    if basedir is None:
        return []
    result = []
    for installation in os.listdir(basedir):
        macho = os.path.join(basedir, installation, "cache/Machonet",
                             TRANQUILITY)
        if not os.path.isdir(macho):
            continue
        result.append(macho)
    return result

def find_cache_basedir():
    for path in CACHEPATHS:
        path = os.path.normpath(os.path.expandvars(path))
        if os.path.isdir(path):
            return path
    return None

def wintime_to_datetime(timestamp):
    return datetime.datetime.utcfromtimestamp(
        (timestamp - 116444736000000000L) / 10000000
        )
