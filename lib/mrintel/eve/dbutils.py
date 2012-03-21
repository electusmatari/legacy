import ConfigParser
import psycopg2

class DBConnection(object):
    def __init__(self):
        conf = ConfigParser.SafeConfigParser()
        conf.read(["/home/forcer/.mrintel.conf"])
        self.conn = psycopg2.connect(host=conf.get('database', 'host'),
                                     user=conf.get('database', 'user'),
                                     password=conf.get('database', 'password'),
                                     database=conf.get('database', 'database'))

    def find_type(self, needle):
        c = self.conn.cursor()
        c.execute("SELECT typename, typeid FROM ccp.invtypes "
                  "WHERE typename ILIKE %s", (needle,))
        if c.rowcount == 1:
            return c.fetchone()
        c.execute("SELECT typename, typeid FROM ccp.invtypes "
                  "WHERE typename ILIKE %s", ("%" + needle + "%",))
        return ([typename for (typename, typeid) in c.fetchall()],
                None)

    def sold_by_npccorps(self, typeid):
        c = self.conn.cursor()
        c.execute("SELECT n.itemname "
                  "FROM ccp.crpnpccorporationtrades t "
                  "     INNER JOIN ccp.invnames n "
                  "       ON t.corporationid = n.itemid "
                  "WHERE typeid = %s",
                  (typeid,))
        return [corpname for (corpname,) in c.fetchall()]

    def baseprice(self, typeid):
        c = self.conn.cursor()
        c.execute("SELECT baseprice "
                  "FROM ccp.invtypes "
                  "WHERE typeid = %s",
                  (typeid,))
        return c.fetchone()[0]

    def marketgroup(self, typeid):
        c = self.conn.cursor()
        c.execute("SELECT marketgroupid "
                  "FROM ccp.invtypes "
                  "WHERE typeid = %s",
                  (typeid,))
        return c.fetchone()[0]

    def itemname(self, itemid):
        c = self.conn.cursor()
        c.execute("SELECT itemname "
                  "FROM ccp.invnames "
                  "WHERE itemid = %s",
                  (itemid,))
        return c.fetchone()[0]

    def stationid2systemname(self, stationid):
        c = self.conn.cursor()
        c.execute("SELECT sys.solarsystemname "
                  "FROM ccp.stastations st "
                  "     INNER JOIN ccp.mapsolarsystems sys "
                  "       ON st.solarsystemid = sys.solarsystemid "
                  "WHERE st.stationid = %s",
                  (stationid,))
        return c.fetchone()[0]

    def pricecheck(self, typeid, sethours=360, regionlimit=None):
        c = self.conn.cursor()
        sql = ("SELECT o.price, o.volremaining, o.regionid, "
               "       o.solarsystemid, o.stationid, u.cachetimestamp "
               "FROM uploader_marketorder o "
               "     INNER JOIN uploader_upload u "
               "       ON o.upload_id = u.id "
               "WHERE o.typeid = %s "
               "  AND NOT o.bid "
               "  AND u.cachetimestamp > NOW() - "
               "                         INTERVAL '{sethours} hours' ")
        args = [typeid]
        if regionlimit is not None:
            sql += "  AND o.regionid IN ({regionfmt})"
            args.extend(regionlimit)
        c.execute(sql.format(sethours=int(sethours),
                             regionfmt=", ".join(["%s"] * len(regionlimit))),
                  args)
        for (price, volremain, regionid, solarsystemid, stationid,
             cachetimestamp) in c.fetchall():
            yield {'price': price,
                   'quantity': volremain,
                   'regionid': regionid,
                   'solarsystemid': solarsystemid,
                   'stationid': stationid,
                   'checked': cachetimestamp}
