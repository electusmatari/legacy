# GRD cost calculator

import collections
import csv

from lib import evedb

db = evedb.connect()

INDEXEXTRA = ["Construction Blocks",
              "Electronic Parts",
              "Guidance System",
              "Hydrogen Batteries",
              "Miniature Electronics",
              "Rocket Fuel",
              "Super Conductors",
              "Transmitter"]

def materialefficiency(typename):
    group = getgroup(typename)
    if group in ('Carrier', 'Dreadnought'):
        return 2
    elif group in ('Construction Components', 'Tool'):
        return 40
    cat = getcategory(typename)
    if cat == 'Module':
        if gettechlevel(typename) == 1:
            return 40
        else:
            return -4
    elif cat == 'Charge':
        if gettechlevel(typename) == 1:
            return 40
        else:
            return -4
    elif cat == 'Ship':
        if gettechlevel(typename) == 1:
            return 10
        else:
            return -4
    else:
        raise RuntimeError("Wut? %r" % typename)

def inventionchance(typename):
    return 0.4

def inventionruns(typename):
    return 10

def safetymargin(typename):
    if gettechlevel(typename) == 2:
        return 1.2
    else:
        return 1

def tech3cost(typename):
    if typename in ('Loki', 'Proteus', 'Tengu'):
        return 186000000
    elif 'Defensive' in typename or 'Offensive' in typename:
        return 70000000
    else:
        return 20000000

def boostercost(typename):
    return 300000

def cost(typename):
    group = getgroup(typename)
    if group == 'Booster':
        return boostercost(typename)
    mats = manufacture(typename)
    techlevel = gettechlevel(typename)
    if techlevel == 2:
        mats += (invention(typename) *
                 (1.0/inventionchance(typename)) *
                 (1.0/inventionruns(typename)))
    elif techlevel == 3:
        return tech3cost(typename)

    total = 0
    for (mat, qty) in mats.items():
        price = getindex(mat)
        if price is None:
            price = cost(mat)
        total += price * qty
    return total * safetymargin(typename)

from lib import evemetrics

_index = None
def getindex(typename):
    global _index
    if _index is None:
        _index = dict((row[0], float(row[1])) for row in list(csv.reader(file('/home/forcer/public_html/eve/gmi/current.txt')))[1:] if row[1] != '')
        prices = evemetrics.get_prices(INDEXEXTRA)
        for tn in INDEXEXTRA:
            _index[tn] = prices[tn].index()
    return _index.get(typename, None)

def manufacture(typename):
    try:
        blueprint = getblueprint(typename)
    except Exception:
        raise RuntimeError("Don't how how to manufacture %r" % typename)
    # Base materials
    mats = Basket()
    mats.update(dict(getmaterials(typename)))
    # Additional requirements
    more = Basket()
    for (reqtype, qty, dpj, recycle) in getrequirements(blueprint,
                                                        'Manufacturing'):
        # If it's not consumed at all, we ignore it
        if dpj < 0.000001:
            continue
        # Recycle means we have to remove the resulting materials
        if recycle > 0:
            mats -= manufacture(reqtype)
        # If less than one is consumed, change the qty for simplicity
        if dpj < 1:
            qty *= dpj
        more[reqtype] += qty
    bwf = wastefactor(blueprint)
    me = materialefficiency(typename)
    if me >= 0:
        wf = bwf * 0.01 * (1.0 / (me + 1))
    else:
        wf = bwf * 0.01 * (1 - me)
    for material in mats:
        mats[material] += int(round(mats[material] * wf))
    return mats + more

def gettechlevel(typename):
    c = db.cursor()
    c.execute("SELECT COALESCE(ta.valuefloat, ta.valueint) "
              "FROM invtypes t "
              "     INNER JOIN dgmtypeattributes ta "
              "       ON t.typeid = ta.typeid "
              "     INNER JOIN dgmattributetypes at "
              "       ON ta.attributeid = at.attributeid "
              "WHERE at.attributename = 'techLevel' "
              "  AND t.typename = %s",
              (typename,))
    if c.rowcount == 0:
        return 
    else:
        return int(c.fetchone()[0])

def getblueprint(typename):
    c = db.cursor()
    c.execute("SELECT bt.typename "
              "FROM invblueprinttypes bp "
              "     INNER JOIN invtypes bt "
              "       ON bp.blueprinttypeid = bt.typeid "
              "     INNER JOIN invtypes pt "
              "       ON bp.producttypeid = pt.typeid "
              "WHERE pt.typename = %s",
              (typename,))
    return c.fetchone()[0]

def wastefactor(bptypename):
    c = db.cursor()
    c.execute("SELECT bp.wastefactor "
              "FROM invblueprinttypes bp "
              "     INNER JOIN invtypes t "
              "       ON bp.blueprinttypeid = t.typeid "
              "WHERE t.typename = %s",
              (bptypename,))
    return c.fetchone()[0]

def getmaterials(typename):
    c = db.cursor()
    c.execute("SELECT mt.typename, tm.quantity "
              "FROM invtypes t "
              "     INNER JOIN invtypematerials tm "
              "       ON t.typeid = tm.typeid "
              "     INNER JOIN invtypes mt "
              "       ON tm.materialtypeid = mt.typeid "
              "WHERE t.typename = %s",
              (typename,))
    return c.fetchall()

def getrequirements(bptypename, activity):
    c = db.cursor()
    c.execute("SELECT rt.typename, tr.quantity, tr.damageperjob, tr.recycle "
              "FROM invtypes bt "
              "     INNER JOIN invblueprinttypes bp "
              "       ON bt.typeid = bp.blueprinttypeid "
              "     INNER JOIN ramtyperequirements tr "
              "       ON bp.blueprinttypeid = tr.typeid "
              "     INNER JOIN ramactivities act "
              "       ON act.activityid = tr.activityid "
              "     INNER JOIN invtypes rt "
              "       ON rt.typeid = tr.requiredtypeid "
              "     INNER JOIN invgroups rg "
              "       ON rg.groupid = rt.groupid "
              "WHERE bt.typename = %s "
              "  AND act.activityname = %s "
              "  AND rg.groupname != 'Data Interfaces'", # evil hack
              (bptypename, activity))
    return c.fetchall()

def invention(typename):
    result = Basket()
    parent = getparenttype(typename)
    if parent is None:
        return result
    blueprint = getblueprint(parent)
    for (reqtype, qty, dpj, recycle) in getrequirements(blueprint,
                                                        'Invention'):
        if dpj < 0.000001:
            continue
        result[reqtype] = qty
    return result

def getparenttype(typename):
    c = db.cursor()
    c.execute("SELECT pt.typename "
              "FROM invtypes t "
              "     INNER JOIN invmetatypes mt "
              "       ON t.typeid = mt.typeid "
              "     INNER JOIN invtypes pt "
              "       ON pt.typeid = mt.parenttypeid "
              "     INNER JOIN invmetagroups mg "
              "       ON mt.metagroupid = mg.metagroupid "
              "WHERE mg.metagroupname = 'Tech II' "
              "  AND t.typename = %s",
              (typename,))
    if c.rowcount == 0:
        return None
    else:
        return c.fetchone()[0]

class Basket(collections.defaultdict):
    def __init__(self, default_factory=lambda: 0, *args, **kwargs):
        super(Basket, self).__init__(default_factory, *args, **kwargs)

    def __add__(self, other):
        d = self.copy()
        for (key, value) in other.items():
            d[key] += value
        return d

    def __sub__(self, other):
        d = self.copy()
        for (key, value) in other.items():
            d[key] -= value
        return d

    def __mul__(self, multiplier):
        d = self.copy()
        for (key, value) in self.items():
            d[key] = value * multiplier
        return d

_getgroup = None
def getgroup(typename):
    global _getgroup
    if _getgroup is None:
        c = db.cursor()
        c.execute("SELECT t.typename, g.groupname "
                  "FROM invtypes t "
                  "     INNER JOIN invgroups g "
                  "       ON t.groupid = g.groupid")
        _getgroup = dict(c.fetchall())
    return _getgroup[typename]

_getcategory = None
def getcategory(typename):
    global _getcategory
    if _getcategory is None:
        c = db.cursor()
        c.execute("SELECT t.typename, c.categoryname "
                  "FROM invtypes t "
                  "     INNER JOIN invgroups g "
                  "       ON t.groupid = g.groupid "
                  "     INNER JOIN invcategories c "
                  "       ON g.categoryid = c.categoryid ")
        _getcategory = dict(c.fetchall())
    return _getcategory[typename]
