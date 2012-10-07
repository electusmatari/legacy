# EVE Central API

import urllib
from xml.etree.ElementTree import fromstring as parse_xml

from lib import evedb
db = evedb.connect()

base_url = "http://eve-central.com/api/"
marketstat_url = base_url + "marketstat"
quicklook_url = base_url + "quicklook"

def marketstat(types, regions=[], hours=None, minQ=None):
    if len(types) == 0:
        return []
    elif len(types) <= 20:
        typenames = {}
        for typename in types:
            typenames[gettypeid(typename)] = typename
        regionids = get_regions(regions)
        args = []
        for typeid in typenames.keys():
            args.append(("typeid", typeid))
        for region in regionids:
            args.append(("regionlimit", region))
        if hours is not None:
            args.append(("hours", hours))
        if minQ is not None:
            args.append(("minQ", hours))
        xml = get(marketstat_url, args)
        return [EveCType(elt, typenames)
                for elt in xml.findall("marketstat/type")]
    else:
        return (marketstat(types[0:20],
                           regions=regions, hours=hours, minQ=minQ)
                +
                marketstat(types[20:],
                           regions=regions, hours=hours, minQ=minQ))

def get(baseurl, args):
    url = "%s?%s" % (baseurl, urllib.urlencode(args))
    data = urllib.urlopen(url).read()
    return parse_xml(data)

class EveCType(object):
    def __init__(self, elt, typenames):
        self.typeid = elt.attrib["id"]
        self.typename = typenames[int(self.typeid)]
        self.all = None
        self.buy = None
        self.sell = None

        for elt in elt.getchildren():
            data = dict((x.tag, float(x.text)) for x in elt.getchildren())
            if elt.tag == "all":
                self.all = data
            elif elt.tag == "buy":
                self.buy = data
            elif elt.tag == "sell":
                self.sell = data

    def __repr__(self):
        return "<EveCType %s>" % self.typeid

def gettypeid(typename):
    c = db.cursor()
    c.execute("""SELECT typeid FROM invtypes
                 WHERE TRIM(typename) ILIKE %s
                   AND published = 1
              """, (typename,))
    if c.rowcount != 1:
        raise RuntimeError("Unknown or ambiguous type %s" % typename)
    return c.fetchone()[0]

def get_regions(names):
    if len(names) == 0:
        return []
    c = db.cursor()
    sql = ("""SELECT itemid FROM invnames
              WHERE itemname IN (%s)
           """ % ", ".join(["%s"] * len(names)))
    c.execute(sql, tuple(names))
    return [regionid for (regionid,) in c.fetchall()]
