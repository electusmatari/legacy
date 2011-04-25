import datetime
import logging

from django.db import connection
from emtools.gmi.models import Index, IndexHistory
from emtools.gmi.index import TYPE_DATA, REFINEABLES_DATA
from emtools.ccpeve.ccpdb import get_typeid

log = logging.getLogger('gmi')

REPUBLIC = ['Heimatar', 'Metropolis', 'Molden Heath']

def update_index():
    now = datetime.datetime.utcnow().date()
    typeids = set(get_typeid(typename)
                  for (typename, rowtype) in TYPE_DATA
                  if rowtype == 'typename')
    republic = get_index(now, typeids, REPUBLIC)
    heimatar = get_index(now, typeids, ['Heimatar'])
    metropolis = get_index(now, typeids, ['Metropolis'])
    moldenheath = get_index(now, typeids, ['Molden Heath'])
    jita = get_index(now, typeids, ['The Forge'])
    last = dict((index.latest.typeid, index.latest)
                for index in Index.objects.all())
    Index.objects.all().delete()
    for typeid in typeids:
        if typeid in last:
            republiclast = last[typeid].republic
            heimatarlast = last[typeid].heimatar
            metropolislast = last[typeid].metropolis
            moldenheathlast = last[typeid].moldenheath
            jitalast = last[typeid].jita
        else:
            (republiclast, heimatarlast, metropolislast,
             moldenheathlast, jitalast) = (0.0, 0.0, 0.0, 0.0, 0.0)

        obj = IndexHistory.objects.create(
            timestamp=now,
            typeid=typeid,
            republic=republic[typeid].index,
            republicvolume=republic[typeid].volume,
            republicchange=(republic[typeid].index / republiclast if republiclast > 0 else None),
            heimatar=heimatar[typeid].index,
            heimatarvolume=heimatar[typeid].volume,
            heimatarchange=(heimatar[typeid].index / heimatarlast if heimatarlast > 0 else None),
            heimatarage=upload_age(now, typeid, 'Heimatar'),
            metropolis=metropolis[typeid].index,
            metropolisvolume=metropolis[typeid].volume,
            metropolischange=(metropolis[typeid].index / metropolislast if metropolislast > 0 else None),
            metropolisage=upload_age(now, typeid, 'Metropolis'),
            moldenheath=moldenheath[typeid].index,
            moldenheathvolume=moldenheath[typeid].volume,
            moldenheathchange=(moldenheath[typeid].index / moldenheathlast if moldenheathlast > 0 else None),
            moldenheathage=upload_age(now, typeid, 'Molden Heath'),
            jita=jita[typeid].index,
            jitavolume=jita[typeid].volume,
            jitachange=(jita[typeid].index / jitalast if jitalast > 0 else None),
            jitaage=upload_age(now, typeid, 'The Forge'))
        if (obj.republic == 0.0 or (obj.jitavolume > 100 and (float(obj.republicvolume) / float(obj.jitavolume)) < 0.01)):
            obj.republic = obj.jita
            obj.save()
        if obj.republic == 0.0:
            log.warning("No sensible index price for %s could be found" %
                        obj.typename)
            obj.republic = get_last_trade(typeid)
            obj.save()
        Index.objects.create(latest=obj)
    add_refineables(now, last)

def add_refineables(now, last):
    now = datetime.datetime.utcnow().date()
    typeids = set(get_typeid(typename)
                  for (typename, rowtype) in REFINEABLES_DATA
                  if rowtype == 'typename')
    index = dict((index.latest.typeid, index.latest)
                 for index in Index.objects.all())
    for typeid in typeids:
        republic = 0
        heimatar = 0
        metropolis = 0
        moldenheath = 0
        jita = 0
        skip = False
        for qty, reqtypeid in refine(typeid):
            if reqtypeid not in index:
                skip = True
                break
            republic += qty * index[reqtypeid].republic
            heimatar += qty * index[reqtypeid].heimatar
            metropolis += qty * index[reqtypeid].metropolis
            moldenheath += qty * index[reqtypeid].moldenheath
            jita += qty * index[reqtypeid].jita
        if skip:
            continue
        obj = IndexHistory.objects.create(
            timestamp=now,
            typeid=typeid,
            republic=republic,
            republicvolume=0,
            republicchange=republic / last[typeid].republic if typeid in last and last[typeid].republic > 0 else None,
            heimatar=heimatar,
            heimatarvolume=0,
            heimatarchange=heimatar / last[typeid].heimatar if typeid in last and last[typeid].heimatar > 0 else None,
            heimatarage=0,
            metropolis=metropolis,
            metropolisvolume=0,
            metropolischange=metropolis / last[typeid].metropolis if typeid in last and last[typeid].metropolis > 0 else None,
            metropolisage=0,
            moldenheath=moldenheath,
            moldenheathvolume=0,
            moldenheathchange=moldenheath / last[typeid].moldenheath if typeid in last and last[typeid].moldenheath > 0 else None,
            moldenheathage=0,
            jita=jita,
            jitavolume=0,
            jitachange=jita / last[typeid].jita if typeid in last and last[typeid].jita > 0 else None,
            jitaage=0)
        Index.objects.create(latest=obj)
    
def refine(typeid):
    c = connection.cursor()
    c.execute("SELECT mat.quantity::float / t.portionsize, "
              "       mat.materialtypeid "
              "FROM ccp.invtypematerials mat "
              "     INNER JOIN ccp.invtypes t "
              "       ON mat.typeid = t.typeid "
              "WHERE t.typeid = %s",
              (typeid,))
    return c.fetchall()

def upload_age(timestamp, typeid, region):
    c = connection.cursor()
    c.execute("SELECT MAX(u.calltimestamp) "
              "FROM gmi_upload u "
              "     INNER JOIN ccp.mapregions r "
              "       ON u.regionid = r.regionid "
              "WHERE r.regionname = %s "
              "  AND u.typeid = %s "
              "  AND u.timestamp < %s + INTERVAL '1 day' ",
              (region, typeid, timestamp))
    upload = c.fetchone()[0]
    if upload is None:
        return None
    else:
        return (timestamp - upload.date()).days

def get_index(timestamp, typeids, regions):
    """
    Return a dictionary mapping these typeids to their index values
    for this date.

    We use the 7d average from that time backwards. If that does not
    exist, we use the 28d average. If that does not exist, either, we
    use 7d/28d index of The Forge. And if that does not exist, we
    return zero values.
    """
    result = {}
    missing = []
    # 7d average
    index = get_single_index(timestamp - datetime.timedelta(days=8),
                             timestamp - datetime.timedelta(days=1),
                             regions)
    for typeid in typeids:
        if typeid in index:
            result[typeid] = IndexEntry(index=index[typeid].index,
                                        volume=index[typeid].volume)
        else:
            missing.append(typeid)
    if len(missing) == 0:
        return result
    # 28d average
    typeids = missing
    missing = []
    index = get_single_index(timestamp - datetime.timedelta(days=29),
                             timestamp - datetime.timedelta(days=1),
                             regions)
    for typeid in typeids:
        if typeid in index:
            result[typeid] = IndexEntry(index=index[typeid].index,
                                        volume=int(index[typeid].volume/4))
        else:
            missing.append(typeid)
    if len(missing) == 0:
        return result
    # 364d average
    typeids = missing
    missing = []
    index = get_single_index(timestamp - datetime.timedelta(days=365),
                             timestamp - datetime.timedelta(days=1),
                             regions)
    for typeid in typeids:
        if typeid in index:
            result[typeid] = IndexEntry(index=index[typeid].index,
                                        volume=int(index[typeid].volume/52))
        else:
            missing.append(typeid)
    if len(missing) == 0:
        return result
    # Give up
    for typeid in missing:
        result[typeid] = IndexEntry(index=0.0, volume=0)
    return result

def get_single_index(start, end, regions):
    c = connection.cursor()
    c.execute("""
SELECT h.typeid,
       SUM(h.avgprice * h.volume) / SUM(h.volume) AS index,
       SUM(h.volume) AS volume
FROM ccpeve_markethistory h
     INNER JOIN ccp.mapregions r ON h.regionid = r.regionid
WHERE h.historydate > %s
  AND h.historydate <= %s
  AND r.regionname IN (%s)
GROUP BY h.typeid
""" % ("%s", "%s", ", ".join(["%s"] * len(regions))),
              [start, end] + regions)
    return dict((typeid, IndexEntry(index=index, volume=volume))
                for (typeid, index, volume) in c.fetchall())

def get_last_trade(typeid):
    c = connection.cursor()
    c.execute("SELECT avgprice "
              "FROM ccpeve_markethistory h "
              "     INNER JOIN ccp.mapregions r ON h.regionid = r.regionid "
              "WHERE r.regionname IN ('The Forge', 'Heimatar') "
              "ORDER BY h.historydate DESC")
    if c.rowcount == 0:
        return 0.0
    else:
        return c.fetchone()[0]


class IndexEntry(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


SCHEDULE = [('gmi-update', update_index, 60*24)]
