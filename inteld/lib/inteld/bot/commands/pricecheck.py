import logging
import urllib

from xml.etree import ElementTree

from django.db import connection

from inteld.bot.error import CommandError

from inteld.utils import find_type, get_marketgroup, get_itemname, get_itemid
from inteld.utils import get_systemregion, get_systemsecurity
from inteld.utils import get_stationsystem

def pricecheck(argname, regions=[], highsec=False):
    typeid, typename = find_type(argname)
    if typename is None:
        raise CommandError("Can't find a type matching '%s'" % argname)
    result = {'typename': typename}

    if get_marketgroup(typeid) is not None:
        try:
            regionids = [get_itemid(r) for r in regions]
        except:
            raise CommandError("Can't find the specified regions")
        price, systemid = pricecheck_local(typeid, regionids, highsec)
        if price is None:
            price, systemid = pricecheck_evecentral(typeid, regionids, highsec)
        if price is None:
            raise CommandError("Can't find a market price for %s" % typename)
        result['region'] = get_itemname(get_systemregion(systemid))
        result['system'] = get_itemname(systemid)
        result['security'] = get_systemsecurity(systemid)
        result['price'] = price
        return result
    else:
        price = pricecheck_faction(typeid)
        if price is None:
            raise CommandError("Can't find %s on the market or on contracts"
                               % typename)
        result['price'] = price
        return result

def pricecheck_local(typeid, regionids, highsec):
    c = connection.cursor()
    c.execute("""
SELECT mo.price, mo.solarsystemid
FROM uploader_marketorder mo
     INNER JOIN ccp.mapsolarsystems s
       ON mo.solarsystemid = s.solarsystemid
WHERE NOT bid
  AND mo.typeid = %%s
  AND mo.regionid IN (%s)
  AND s.security >= %%s
  AND mo.cachetimestamp > NOW() - INTERVAL '3 days'
ORDER BY price ASC
LIMIT 1
""" % (", ".join(["%s"] * len(regionids))),
              [typeid] + list(regionids) + [0.45 if highsec else -1.0])
    if c.rowcount > 0:
        return c.fetchone()
    else:
        return None, None

def pricecheck_evecentral(typeid, regionids, highsec):
    url = "http://api.eve-central.com/api/quicklook?typeid=%s" % typeid
    for rid in regionids:
        url += "&regionlimit=%s" % rid

    try:
        data = urllib.urlopen(url).read()
        tree = ElementTree.fromstring(data)
    except:
        logging.exception("Exception during eve-central price check")
        return None, None
    for order in tree.findall("quicklook/sell_orders/order"):
        stationid = int(order.find("station").text)
        systemid = get_stationsystem(stationid)
        if highsec:
            security = get_systemsecurity(systemid)
            if security < 0.45:
                continue
        return float(order.find("price").text), systemid
    return None, None

def pricecheck_faction(typeid):
    try:
        u = urllib.urlopen("http://prices.c0rporation.com/faction.xml")
        tree = ElementTree.fromstring(u.read())
    except:
        logging.exception("Exception during query of faction prices")
        return None
    for row in tree.findall("result/rowset/row"):
        if row.attrib['typeID'] == str(typeid):
            return float(row.attrib['avg'])
    return None
