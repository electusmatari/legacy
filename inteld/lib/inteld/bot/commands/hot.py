import datetime

from django.db import connection

from emtools.ccpeve.models import apiroot

def find_hot_systems(regions, include_highsec=False, count=10):
    sql = """
SELECT sys.solarsystemid, sys.solarsystemname, sys.security
FROM ccp.mapsolarsystems sys
     INNER JOIN ccp.mapregions r
       ON sys.regionid = r.regionid
WHERE """
    conditions = []
    args = []
    if len(regions) > 0:
        conditions.append("LOWER(r.regionname) IN (%s)" %
                          (", ".join(["LOWER(%s)"] * len(regions)),))
        args.extend(regions)
    if not include_highsec:
        conditions.append("sys.security < 0.45")
    c = connection.cursor()
    c.execute(sql + " AND ".join(conditions),
              args)
    wanted_systems = dict((sysid, (name, security))
                          for (sysid, name, security) in c.fetchall())
    api = apiroot()
    kills = api.map.Kills()
    result = []
    for sys in kills.solarSystems:
        if sys.shipKills > 0 and sys.solarSystemID in wanted_systems:
            name, security = wanted_systems[sys.solarSystemID]
            result.append((sys.shipKills, name, security))
    return (sorted(result, key=lambda x: (-x[0], x[2]))[:count],
            datetime.datetime.utcfromtimestamp(kills._meta.cachedUntil))
