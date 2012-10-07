import psycopg2
from psycopg2.extensions import register_adapter
import sdb
from sdb.orm import setdefaultdb, DBTable

def connect():
    conn = sdb.connect(psycopg2, database="eve")
    setdefaultdb(conn)
    c = conn.cursor()
    c.execute('SET search_path TO "$user",public,ccp')
    return conn

class invTypes(DBTable):
    class Meta:
        table = "ccp.invtypes"
        pk = "typeid"

class mapRegions(DBTable):
    class Meta:
        table = "ccp.mapregions"
        pk = "regionid"

class mapSolarSystems(DBTable):
    class Meta:
        table = "ccp.mapsolarsystems"
        pk = "solarsystemid"

class mapDenormalize(DBTable):
    class Meta:
        table = "ccp.mapdenormalize"
        pk = "itemid"

class chrFactions(DBTable):
    class Meta:
        table = "ccp.chrfactions"
        pk = "factionid"

class PGName(object):
    def __init__(self, name):
        """
        A PostgreSQL Name object

        This can be used to represent table or row names.
        """
        self.name = name

    def getquoted(self):
        return '"%s"' % self.name.replace('"', r'\"')

    def __repr__(self):
        return "<PGName %s>" % self.getquoted()

register_adapter(PGName, lambda x: x)
