import datetime
import urllib
import xml.etree.ElementTree as ET
import evelib.newdb as evedb

import sys
import time

def call(apiname, args):
    url = ("http://eve-metrics.com/api/%s.xml?%s"
           % (apiname, urllib.urlencode(args)))
    tree = None
    tries = 0
    while tree is None:
        try:
            tree = ET.fromstring(urllib.urlopen(url).read())
        except Exception as e:
            sys.stderr.write("Error %s while retrieving %s: %s\n" %
                             (e.__class__.__name__,
                              url,
                              str(e)))
            tries += 1
            if tries >= 10:
                raise
            time.sleep(5)
    return tree

def history(types, days=None, regions=None, key=None):
    typeobjs = {}
    regionobjs = {}
    type_ids = []
    for name in types:
        typeobj = evedb.invTypes.get(typename=name)
        typeobjs[typeobj.typeid] = typeobj
        type_ids.append(typeobj.typeid)
    args = {"type_ids": ",".join([str(x) for x in type_ids])}
    if days is not None:
        args["days"] = str(days)
    if regions is not None:
        region_ids = []
        for name in regions:
            regionobj = evedb.mapRegions.get(regionname=name)
            regionobjs[regionobj.regionid] = regionobj
            region_ids.append(regionobj.regionid)
        args["region_ids"] = ",".join([str(x) for x in region_ids])
    if key is not None:
        args["key"] = key
    tree = call("history", args)
    result = []
    for typeelt in tree.findall("type"):
        typeid = int(typeelt.attrib["id"])
        for regionelt in typeelt.findall("region"):
            regionid = int(regionelt.attrib["id"])
            historyelt = regionelt.find("history")
            for dayelt in historyelt.findall("day"):
                avg = float(dayelt.attrib["average"])
                max = float(dayelt.attrib["maximum"])
                min = float(dayelt.attrib["minimum"])
                mov = long(dayelt.attrib["movement"])
                orders = long(dayelt.attrib["orders"])
                day = datetime.datetime.strptime(dayelt.text, "%Y-%m-%d")
                result.append((day, regionobjs[regionid], typeobjs[typeid],
                               orders, mov, max, avg, min))
    return result
