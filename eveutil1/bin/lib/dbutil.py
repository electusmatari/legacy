from collections import defaultdict
import sys

import psycopg2

import evedb
import characters

db = evedb.connect()

def materials(typename):
    c = db.cursor()
    c.execute("SELECT mt.typeName, m.quantity "
              "FROM ccp.invTypeMaterials m "
              "     INNER JOIN ccp.invTypes t "
              "       ON m.typeID = t.typeID "
              "     INNER JOIN ccp.invTypes mt "
              "       ON m.materialTypeID = mt.typeID "
              "WHERE t.typeName = %s",
              (typename,))
    return c.fetchall()

def manufacture(typename, me=None):
    c = db.cursor()
    c.execute("SELECT typeID, portionSize "
              "FROM ccp.invTypes "
              "WHERE typeName = %s",
              (typename,))
    if c.rowcount != 1:
        raise RuntimeError, "Can't find type %r" % typename
    (typeid, portionsize) = c.fetchone()
    c.execute("SELECT blueprinttypeid, wastefactor "
              "FROM ccp.invblueprinttypes "
              "WHERE producttypeid = %s",
              (typeid,))
    if c.rowcount != 1:
        return None
    (bptypeid, wastefactor) = c.fetchone()
    components = materials(typename)
    c.execute("SELECT reqt.typeName, tr.quantity, tr.damagePerJob, tr.recycle "
              "FROM ccp.ramTypeRequirements tr "
              "     INNER JOIN ccp.invTypes reqt "
              "       ON tr.requiredTypeID = reqt.typeID "
              "     INNER JOIN ccp.ramActivities act "
              "       ON tr.activityID = act.activityID "
              "WHERE act.activityName = 'Manufacturing' "
              "  AND tr.damagePerJob > 0 "
              "  AND tr.typeID = %s ",
              (bptypeid,))
    typereqs = []
    components = dict(components)
    for (name, qty, dpj, recycle) in c.fetchall():
        typereqs.append((name, qty, dpj))
        if recycle == 1:
            for (tn, qty) in materials(name):
                if tn in components:
                    components[tn] -= qty
    components = [(tn, qty) for (tn, qty) in components.items()
                  if qty > 0]
    if me is not None:
        components = [(name, round(quantity * (1 + ((wastefactor / 100.0)
                                                    / (1 + me)))))
                      for (name, quantity) in components]
    return ([(name, qty/float(portionsize), 1.0) for (name, qty) in components]
            +
            [(name, qty/float(portionsize), dpj) for (name, qty, dpj)
             in typereqs])

def cost(typename, index, get_me=lambda x: 0):
    c = db.cursor()
    agenda = [(typename, 1, 1.0)]
    cost = defaultdict(lambda: 0)
    while len(agenda) > 0:
        (this, agenda) = (agenda[0], agenda[1:])
        (typename, quantity, dpj) = this
        if typename in index:
            cost[typename] += quantity * dpj
            continue
        manuf = manufacture(typename, get_me(typename))
        if manuf is not None and len(manuf) > 0:
            agenda.extend([(manuf_tn, manuf_qty * quantity, manuf_dpj * dpj)
                           for (manuf_tn, manuf_qty, manuf_dpj)
                           in manuf])
            continue
        c.execute("SELECT baseprice FROM ccp.invtypes WHERE typename = %s",
                  (typename,))
        sys.stderr.write("Using base price for %s\n" % (typename,))
        index[typename] = c.fetchone()[0]
        cost[typename] += quantity * dpj
    return [(typename, qty, index[typename] * qty)
            for (typename, qty) in cost.items()]

def ensure_characterids(idlist):
    idlist = [int(x) for x in idlist]
    db = psycopg2.connect(database="eve")
    c = db.cursor()
    c.execute("SELECT id, name FROM api_names WHERE id IN (%s)"
              % (",".join(["%s"] * len(idlist))),
              idlist)
    found = dict(c.fetchall())
    toget = [str(x) for x in idlist if x not in found]
    if len(toget) == 0:
        return
    api = characters.api()
    result = api.eve.CharacterName(ids=",".join(toget))
    for row in result.characters:
        c.execute("INSERT INTO api_names (id, name) VALUES (%s, %s)",
                  (row.characterID, row.name))
    db.commit()

def ensure_characternames(namelist):
    db = psycopg2.connect(database="eve")
    c = db.cursor()
    c.execute("SELECT id, name FROM api_names WHERE name IN (%s)"
              % (",".join(["%s"] * len(namelist))),
              namelist)
    found = dict(c.fetchall())
    toget = [x for x in namelist if x not in found]
    if len(toget) == 0:
        return
    api = characters.api()
    result = api.eve.CharacterID(names=",".join(toget))
    for row in result.characters:
        c.execute("INSERT INTO api_names (id, name) VALUES (%s, %s)",
                  (row.characterID, row.name))
    db.commit()
