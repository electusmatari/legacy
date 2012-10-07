#!/usr/bin/env python

import MySQLdb
import psycopg2
import sys
sys.path.append("/home/forcer/Projects/evecode/web/electusmatari.com/data/python/emtools/ccpeve")
import eveapi
api = eveapi.EVEAPIConnection()

ccp = psycopg2.connect(host="localhost", database="eve", user="emtools")
c = ccp.cursor()
c.execute("select typeid from ccp.invtypes")
real_typeids = set(typeid for (typeid,) in c.fetchall())

execfile("/home/forcer/Projects/private/old_access.py")

kb = MySQLdb.connect(host=db_host, user=db_user,
                     passwd=db_pass, db="emkillboard")
c = kb.cursor()
c.execute("select itt_id from kb3_item_types")
kb_typeids = set(typeid for (typeid,) in c.fetchall())
fake_typeids = kb_typeids - real_typeids
print("{0} fake typeids".format(len(fake_typeids)))
typeids = list(kb_typeids & real_typeids)

bunch_list = [typeids[x:x+200] for x in range(0, len(typeids), 200)]
mapping = {}

for bunch in bunch_list:
    result = api.eve.TypeName(ids=",".join(str(x) for x in bunch))
    for row in result.types:
        if len(row.typeName.strip()) > 0:
            mapping[row.typeID] = row.typeName

missing = set(typeids) - set(mapping.keys())
print("Missing {0} type names.".format(len(missing)))

for typeid, typename in mapping.items():
    c.execute("UPDATE kb3_item_types SET itt_name = %s WHERE itt_id = %s",
              (typename, typeid))


c.execute("select typeID from kb3_invtypes")
kb_typeids = set(typeid for (typeid,) in c.fetchall())
fake_typeids = kb_typeids - real_typeids
print("{0} fake typeids".format(len(fake_typeids)))
typeids = list(kb_typeids & real_typeids)

bunch_list = [typeids[x:x+200] for x in range(0, len(typeids), 200)]
mapping = {}

for bunch in bunch_list:
    result = api.eve.TypeName(ids=",".join(str(x) for x in bunch))
    for row in result.types:
        if len(row.typeName.strip()) > 0:
            mapping[row.typeID] = unicode(row.typeName)

missing = set(typeids) - set(mapping.keys())
print("Missing {0} type names.".format(len(missing)))

for typeid, typename in mapping.items():
    c.execute("UPDATE kb3_invtypes SET typename = %s WHERE typeid = %s",
              (typename.encode("utf-8"), typeid))
kb.commit()
