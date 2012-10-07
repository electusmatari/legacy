import collections
import datetime
import urllib
import xml.etree.ElementTree as ElementTree
import xml.parsers.expat as expat
import time

import lib.evedb as evedb

db = evedb.connect()

# num regionids * num typeids <= 25
MAX_HISTORY_PRODUCT = 25

REPUBLIC_REGIONS = ['Heimatar', 'Metropolis', 'Molden Heath']
OTHER_REGIONS = ['The Forge']

class EveMetrics(object):
    def __init__(self, base_url="http://eve-metrics.com/api"):
        self.base_url = base_url

    def call(self, method, args):
        url = "%s/%s.xml?%s" % (self.base_url, method, urllib.urlencode(args))
        while True:
            try:
                data = urllib.urlopen(url).read()
                return ElementTree.fromstring(data)
            except expat.ExpatError:
                time.sleep(5)

    def history(self, regionnames, typenames):
        regionids = [str(regionname2id(name)) for name in regionnames]
        typeids = [str(typename2id(name)) for name in typenames]
        typeids_per_call = MAX_HISTORY_PRODUCT / len(regionids)
        if typeids_per_call == 0:
            raise RuntimeException("Too many regionids")
        result = []
        while len(typeids) > 0:
            this_typeids = typeids[:typeids_per_call]
            typeids = typeids[typeids_per_call:]
            etree = self.call("history", [("region_ids", ",".join(regionids)),
                                          ("type_ids", 
                                           ",".join(this_typeids))])
            result.extend([TypeHistory(subtree) for subtree
                           in etree.findall("type")])
        return result

class TypeHistory(object):
    def __init__(self, etree):
        self.typeid = int(etree.attrib['id'])
        self.typename = etree.find('name').text
        self.regions = [RegionTypeHistory(subtree) for subtree
                        in etree.findall("region")]

class RegionTypeHistory(object):
    def __init__(self, etree):
        self.regionid = int(etree.attrib['id'])
        self.regionname = etree.find("name").text
        lu = etree.find("last_upload").text
        if lu is None:
            self.last_upload = None
        else:
            self.last_upload = datetime.datetime.strptime(
                lu,
                "%Y-%m-%d %H:%M:%S +0000")
        self.days = [DayTypeHistory(subtree) for subtree
                     in etree.find("history").findall("day")]

class DayTypeHistory(object):
    def __init__(self, etree):
        self.day = datetime.datetime.strptime(etree.text, "%Y-%m-%d")
        self.average = float(etree.attrib['average'])
        self.maximum = float(etree.attrib['maximum'])
        self.minimum = float(etree.attrib['minimum'])
        self.movement = int(etree.attrib['movement'])
        self.orders = int(etree.attrib['orders'])

tn2id = None
tid2n = None

def typename2id(name):
    if tn2id is None:
        build_types()
    return tn2id[name]

def typeid2name(id):
    if tid2n is None:
        build_types()
    return tid2n[id]

def build_types():
    global tn2id
    global tid2n
    tn2id = {}
    tid2n = {}
    c = db.cursor()
    c.execute("SELECT typeid, typename FROM invtypes")
    for tid, tn in c.fetchall():
        tn2id[tn] = tid
        tid2n[tid] = tn

rn2id = None

def regionname2id(name):
    global rn2id
    if rn2id is None:
        rn2id = {}
        c = db.cursor()
        c.execute("SELECT regionname, regionid FROM mapregions")
        for rn, rid in c.fetchall():
            rn2id[rn] = rid
    return rn2id.get(name, name)

def get_prices(typenames, regions=REPUBLIC_REGIONS + OTHER_REGIONS):
    emtr = EveMetrics()
    prices = dict((typename, Type(typename)) for typename in typenames)
    for th in emtr.history(regions,
                           typenames):
        for reg in th.regions:
            for day in reg.days:
                prices[th.typename].add_history(reg.regionname,
                                                day.day, day.average,
                                                day.movement)
            prices[th.typename].add_last_upload(reg.regionname,
                                                reg.last_upload)
    return prices

class Type(object):
    def __init__(self, typename):
        self.typename = typename
        self.regions = collections.defaultdict(lambda: [])
        self._last_upload = {}

    def add_history(self, region, day, average, movement):
        self.regions[region].append((day, average, movement))
        self.regions[region].sort(reverse=True) # by date, newest first

    def add_last_upload(self, regionname, last_upload):
        self._last_upload[regionname] = last_upload

    def last_upload(self):
        return self._last_upload

    def movement(self, regions=None, days=7):
        now = datetime.datetime.utcnow()
        total_movement = 0
        if regions is None:
            regions = self.regions.keys()
        for reg in regions:
            for (day, average, movement) in self.regions[reg][0:days]:
                if (now - day).days <= days:
                    total_movement += movement
        return total_movement

    def change(self, regions=None):
        d7index = self.index(regions=regions)
        d1index = self.last(regions=regions)
        if d7index == 0:
            return 1.0
        else:
            return (d1index / d7index) - 1

    def last(self, regions=None, do_jita=True):
        now = datetime.datetime.utcnow()
        total = 0
        total_movement = 0
        if regions is None:
            regions = self.regions.keys()
        for reg in regions:
            if len(self.regions[reg]) > 0:
                (day, average, movement) = self.regions[reg][0]
                total += average * movement
                total_movement += movement
        if total_movement > 0:
            return float(total) / total_movement
        if do_jita:
            return self.last(regions=['The Forge'], do_jita=False)
        else:
            return 0.0

    def index(self, regions=None, days=7, do_jita=True):
        """
        Return the index price for this type.
        """
        now = datetime.datetime.utcnow()
        total = 0
        total_movement = 0
        if regions is None:
            regions = self.regions.keys()
        for reg in regions:
            for (day, average, movement) in self.regions[reg][0:days]:
                if (now - day).days <= days:
                    total += average * movement
                    total_movement += movement

        if total_movement > 0:
            return float(total) / total_movement
        if do_jita:
            return self.index(regions=['The Forge'], days=days,
                              do_jita=False)
        else:
            return 0.0
