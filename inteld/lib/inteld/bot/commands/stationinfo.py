import re

from django.db import connection

from inteld.bot.error import CommandError
from inteld.utils import get_itemid, get_itemname, get_systemstations

def systeminfo(systemname):
    systemid = get_itemid(systemname)
    if systemid is None:
        raise CommandError("System '%s' not found" % systemname)
    systemname = get_itemname(systemid)
    desc_list = []
    for stationid in get_systemstations(systemid):
        name = stationabbrev(stationid)
        desc = []
        if is_insta_redock(stationid):
            desc.append("insta-redock")
        else:
            desc.append("non-insta-redock")
        locator_list = get_locator_levels(stationid)
        if len(locator_list) > 0:
            desc.append("L%s locator" % max(locator_list))
        services = get_station_services(stationid)
        if 'Repair Facilities' not in services:
            desc.append("no repair")
        desc_list.append("\x02%s\x02 (%s)" % (name, ", ".join(desc)))
    return "%s: %s" % (systemname, ", ".join(desc_list))

def stationinfo(systemname, station):
    stationid = station_unabbrev(systemname, station)
    stationname = get_itemname(stationid)
    typename = get_station_type(stationid)
    if is_insta_redock(stationid):
        redock = 'insta-redock'
    else:
        redock = 'non-insta-redock'
    services = get_station_services(stationid)
    locator_levels = sorted(get_locator_levels(stationid))
    desc = "\x02%s\x02 (%s - \x02%s\x02)" % (stationname, typename, redock)
    if len(locator_levels) > 1:
        desc += (", locator levels %s" %
                 ", ".join(str(x) for x in locator_levels))
    elif len(locator_levels) == 1:
        desc += (", L%s locator" %
                 ", ".join(str(x) for x in locator_levels))
    if len(services):
        desc += ", %s" % ", ".join(services)
    return desc

STATION_MOON_RX = re.compile("([IVX]+) .*- Moon ([0-9]+) .*")
STATION_NOMOON_RX = re.compile("([IVX]+) .*")

INSTA_REDOCK = ['Minmatar Hub',
                'Minmatar Industrial Station',
                'Minmatar Military Station',
                'Minmatar Mining Station',
                'Station (Gallente 1)',
                'Station (Gallente 2)',
                'Station ( Gallente 3 )',
                'Station ( Gallente 4 )',
                'Station ( Gallente 6 )',
                'Station ( Gallente 7 )',
                'Station ( Gallente 8 )',
                'Caldari Food Processing Plant Station',
                'Station (Caldari 1)',
                'Station (Caldari 2)',
                'Station (Caldari 3)',
                'Station ( Caldari 5 )',
                'Station ( Caldari 6 )',
                'Concord Starbase',
                'Amarr Mining Station',
                'Amarr Research Station',
                'Amarr Station Hub',
                'Amarr Station Military',
                'Amarr Trade Post'
                ]

def stationabbrev(stationid):
    c = connection.cursor()
    c.execute("SELECT sys.solarsystemname, "
              "       st.stationname "
              "FROM ccp.mapsolarsystems sys "
              "     INNER JOIN ccp.stastations st "
              "       ON sys.solarsystemid = st.solarsystemid "
              "WHERE st.stationid = %s",
              (stationid,))
    systemname, stationname = c.fetchone()
    nosystem = stationname.lstrip(systemname).strip()
    match = STATION_MOON_RX.match(nosystem)
    if match is not None:
        planet, moon = match.groups()
        return "%s-%s" % (planet, moon)
    match = STATION_NOMOON_RX.match(nosystem)
    if match is not None:
        planet, = match.groups()
        return planet
    return stationname

def station_unabbrev(systemname, abbrev):
    c = connection.cursor()
    if "-" in abbrev:
        planet, moon = abbrev.split("-")
        planet = planet.upper()
        c.execute("SELECT stationid FROM ccp.stastations "
                  "WHERE stationname ILIKE %s",
                  ("%s %s %% Moon %s %%" % (systemname, planet, moon),))
        if c.rowcount == 0:
            raise CommandError("Station on %s %s-%s not found" % (systemname,
                                                                  planet,
                                                                  moon))
    else:
        planet = abbrev
        planet = planet.upper()
        c.execute("SELECT stationid FROM ccp.stastations "
                  "WHERE stationname ILIKE %s "
                  "AND stationname NOT LIKE '%%Moon%%'",
                  ("%s %s %%" % (systemname, planet),))
        if c.rowcount == 0:
            raise CommandError("Station on %s %s not found" % (systemname,
                                                               planet))
    return c.fetchone()[0]

def is_insta_redock(stationid):
    if get_station_type(stationid) in INSTA_REDOCK:
        return True
    else:
        return False

def get_station_type(stationid):
    c = connection.cursor()
    c.execute("SELECT t.typename "
              "FROM ccp.stastations st "
              "     INNER JOIN ccp.invtypes t "
              "       ON st.stationtypeid = t.typeid "
              "WHERE st.stationid = %s",
              (stationid,))
    (typename,) = c.fetchone()
    return typename

def get_locator_levels(stationid):
    c = connection.cursor()
    c.execute("""
SELECT a.level
FROM ccp.agtagents a
WHERE a.locationid = %s
  AND a.islocator = 1
""", (stationid,))
    return [level for (level,) in c.fetchall()]

def get_station_services(stationid):
    c = connection.cursor()
    c.execute("""
SELECT s.serviceName
FROM ccp.stastations st
     INNER JOIN ccp.staoperationservices sos
       ON st.operationid = sos.operationid
     INNER JOIN ccp.staservices s
       ON sos.serviceid = s.serviceid
WHERE st.stationid = %s
  AND s.servicename IN ('Repair Facilities', 'Factory', 'Laboratory',
                        'Cloning')
""", (stationid,))
    return [servicename for (servicename,) in c.fetchall()]
