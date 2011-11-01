from emtools.ccpeve.models import apiroot, APIKey
from emtools.ccpeve import eveapi

from django.db import connection

def find_type(typename):
    c = connection.cursor()
    c.execute("SELECT typeid, typename FROM ccp.invtypes "
              "WHERE published = 1 AND LOWER(typename) = LOWER(%s)",
              (typename.strip(),))
    if c.rowcount == 1:
        return c.fetchone()
    c.execute("SELECT typeid, typename FROM ccp.invtypes "
              "WHERE typename ILIKE %s "
              "ORDER BY CHAR_LENGTH(typename) ASC, LOWER(typename) ASC",
              ("%%%s%%" % typename,))
    if c.rowcount < 1:
        return None, None
    else:
        return c.fetchone()

def get_itemname(itemid):
    c = connection.cursor()
    c.execute("SELECT itemname FROM ccp.evenames WHERE itemid = %s",
              (itemid,))
    if c.rowcount < 1:
        raise RuntimeError("Item %s not found" % itemid)
    else:
        return c.fetchone()[0]

def get_itemid(itemname):
    c = connection.cursor()
    c.execute("SELECT itemid FROM ccp.evenames "
              "WHERE LOWER(itemname) = LOWER(%s)",
              (itemname,))
    if c.rowcount < 1:
        return None
    else:
        return c.fetchone()[0]

def get_marketgroup(typeid):
    c = connection.cursor()
    c.execute("SELECT marketgroupid "
              "FROM ccp.invtypes "
              "WHERE typeid = %s",
              (typeid,))
    if c.rowcount > 0:
        return c.fetchone()[0]
    else:
        raise RuntimeError('Type %s not found' % (typeid,))

def get_systemregion(systemid):
    c = connection.cursor()
    c.execute("SELECT regionid FROM ccp.mapsolarsystems WHERE "
              "solarsystemid = %s", (systemid,))
    if c.rowcount < 1:
        raise RuntimeError("System %s not found" % (systemid,))
    else:
        return c.fetchone()[0]

def get_systemsecurity(systemid):
    c = connection.cursor()
    c.execute("SELECT security FROM ccp.mapsolarsystems WHERE "
              "solarsystemid = %s", (systemid,))
    if c.rowcount < 1:
        raise RuntimeError("System %s not found" % (systemid,))
    else:
        return c.fetchone()[0]

def get_stationsystem(stationid):
    c = connection.cursor()
    c.execute("SELECT solarsystemid FROM ccp.stastations "
              "WHERE stationid = %s",
              (stationid,))
    if c.rowcount == 0:
        raise RuntimeError("Station %s not found" % (stationid,))
    else:
        return c.fetchone()[0]

def floatcomma(num):
    s = "%.2f" % num
    pre, post = s.split(".")
    return "%s.%s" % (intcomma(int(pre)), post)

def intcomma(s):
    s = str(s)
    return ",".join([s[idx-3:idx] 
                     for idx in reversed(range(-3, -len(s), -3))] +
                    [s[-3:]])

def get_ownerid(arg):
    api = apiroot()
    try:
        charid = api.eve.CharacterID(names=arg).characters[0].characterID
        if charid == 0:
            return None
        return charid
    except eveapi.Error as e:
        if e.code == 122: # Invalid or missing list of names
            return None
        raise
    except NameError: # Encoding error
        return None
    except UnicodeEncodeError:
        return None

def get_ownername(arg):
    api = apiroot()
    try:
        return api.eve.CharacterName(ids=arg).characters[0].name
    except:
        return None

def get_standings():
    key = APIKey.objects.get(name='Gradient').corp()
    kcl = key.ContactList()
    return dict((row.contactID, row.standing)
                for row in kcl.allianceContactList)

def sizestring(nbytes):
    units = [' b', ' kB', ' MB', ' GB', ' TB']
    nbytes = float(nbytes)
    for rank, unit in enumerate(units):
        if nbytes < 1000 ** (rank+1):
            return "%.1f%s" % ((nbytes / float(1024**rank)), unit)
    return nbytes

def plural(num, ifplural="s", ifsingular=""):
    if num == 1:
        return ifsingular
    else:
        return ifplural
