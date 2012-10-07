import heapq

from django.db import connection

from inteld.utils import get_systemsecurity
from inteld.bot.error import CommandError

def find_route(startname, destname, avoidlist=[], safer=False):
    destid, destname = find_system(destname)
    startid, startname = find_system(startname)
    startsec = get_systemsecurity(startid)
    agenda = [(0, [(startname, startsec)], startid)]
    avoidset = set()
    for name in avoidlist:
        avoidset.add(find_system(name)[0])
    neighborhood = get_neighborhood()
    visited = set()
    while len(agenda) > 0:
        (cost, route, hereid) = heapq.heappop(agenda)
        if hereid == destid:
            return route
        if hereid in visited or hereid in avoidset:
            continue
        visited.add(hereid)
        for neighborid, neighborname, neighborsec in neighborhood[hereid]:
            if safer and neighborsec < 0.45:
                neighborcost = cost + 1 + 50
            else:
                neighborcost = cost + 1
            neighborroute = route + [(neighborname, neighborsec)]
            heapq.heappush(agenda, (neighborcost, neighborroute, neighborid))
    return None

def get_neighborhood():
    c = connection.cursor()
    c.execute("""
SELECT j.fromsolarsystemid,
       j.tosolarsystemid,
       s.solarsystemname,
       s.security
FROM ccp.mapsolarsystemjumps j
     INNER JOIN ccp.mapsolarsystems s
       ON j.tosolarsystemid = s.solarsystemid
""")
    jumps = {}
    for fromid, toid, toname, tosecurity in c.fetchall():
        jumps.setdefault(fromid, [])
        jumps[fromid].append((toid, toname, tosecurity))
    return jumps

def find_system(name):
    c = connection.cursor()
    c.execute("SELECT solarsystemid, solarsystemname "
              "FROM ccp.mapsolarsystems "
              "WHERE LOWER(solarsystemname) = LOWER(%s)",
              (name,))
    if c.rowcount == 1:
        return c.fetchone()
    c.execute("SELECT solarsystemid, solarsystemname "
              "FROM ccp.mapsolarsystems "
              "WHERE solarsystemname ILIKE %s",
              ("%%%s%%" % name,))
    if c.rowcount < 1:
        raise CommandError("Can't find a system matching '%s'" % name)
    elif c.rowcount > 1:
        raise CommandError("More than one system matching '%s' found" % name)
    else:
        return c.fetchone()
