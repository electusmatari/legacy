#!/usr/bin/env python

# CachedMethodCalls\bfbd.cache

import datetime
import sys

import smbc

import reverence.blue

import evelib.newdb as db

def main():
    conn = db.connect()
    c = conn.cursor()
    c.execute("select factionid, factionname from ccp.chrfactions")
    facid2name = dict(c.fetchall())
    c.execute("select solarsystemid, solarsystemname from ccp.mapsolarsystems")
    sysid2name = dict(c.fetchall())

    if len(sys.argv) == 1:
        f = getfile()
    else:
        f = file(sys.argv[1])

    data = reverence.blue.marshal.Load(f.read())
    result = []
    for facid in data[1]['lret']:
        for sysid, threshold, current in data[1]['lret'][facid]['defending']:
            if current == 0:
                continue
            result.append((facid2name[facid], sysid2name[sysid],
                           threshold, current))
    print "Cached from: %s" % wintime_to_datetime(data[1]['version'][0]).strftime("%Y-%m-%d %H:%M")
    lastfaction = None
    for faction, system, threshold, vp in sorted(result,
                                                 key=lambda x: (x[0], -x[3], x[1])):
        if faction != lastfaction:
            print
            print faction
            print "=" * len(faction)
            lastfaction = faction
        print "%-17s  %5i / %5i (%6.2f%%)" % (
            system, vp, threshold, (vp / float(threshold)) * 100)

def wintime_to_datetime(timestamp):
    return datetime.datetime.utcfromtimestamp(
        (timestamp - 116444736000000000L) / 10000000
        )

def getfile():
    import smbc
    import subprocess
    import StringIO
    base = "//forcix/$ccpeve"
    path = "c_programme_ccp_eve_tranquility/cache/MachoNet/87.237.38.200"
    ctx = smbc.Context()
    verdir = max([int(d.name) for d in 
                  ctx.opendir("smb:%s/%s" % (base, path)).getdents()
                  if d.name.isnumeric()])
    args = ["smbclient", "-N", base, "-c",
            "cd %s/%s/CachedMethodCalls ; get bfbd.cache -" % (path, verdir)]
    return StringIO.StringIO(subprocess.check_output(args, stderr=open("/dev/null")))

if __name__ == '__main__':
    main()
