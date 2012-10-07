# eve-kill

import datetime
import urllib
from evelib import eveapi
import evelib.newdb as db

def getfeed(feedurl, lastkillid=0, master=True):
    return lastkillid, []
    killid = lastkillid
    result = []
    for ignored in range(10):
        newlastkillid, killmails = apifeed("%s&lastintID=%s" %
                                           (feedurl, lastkillid))
        killid = max(killid, newlastkillid)
        result.extend(killmails)
        if len(killmails) < 100:
            break
    return killid, result

def apifeed(url):
    kill_list = eveapi.ParseXML(urllib.urlopen(url)).kills
    killmails = []
    lastkillid = 0
    for kill in kill_list:
        lastkillid = max(lastkillid, kill.killInternalID)
        killmails.append(unparse_killinfo(kill))
    return lastkillid, killmails

def unparse_killinfo(kill):
    lines = []
    lines.append(datetime.datetime.utcfromtimestamp(
            kill.killTime).strftime("%Y.%m.%d %H:%M:%S"))
    lines.append("")

    lines.append("Victim: %s" % kill.victim.characterName)
    lines.append("Corp: %s" % kill.victim.corporationName)
    if kill.victim.allianceID == 0:
        lines.append("Alliance: Unknown")
    else:
        lines.append("Alliance: %s" % kill.victim.allianceName)
    if kill.victim.factionID == 0:
        lines.append("Faction: Unknown")
    else:
        lines.append("Faction: %s" % kill.victim.factionName)
    lines.append("Destroyed: %s" % typeid2name(kill.victim.shipTypeID))
    lines.append("System: %s" % systemid2name(kill.solarSystemID))
    lines.append("Security: %s" % systemid2sec(kill.solarSystemID))
    lines.append("Damage Taken: %s" % kill.victim.damageTaken)
    lines.append("")
    lines.append("Involved parties:")
    # if kill.moonID (== 0)
    for attacker in kill.attackers:
        lines.append("")
        if attacker.finalBlow:
            fb = " (laid the final blow)"
        else:
            fb = ""
        if is_npc_corp(attacker.corporationID):
            lines.append("Name: %s / %s%s" % (attacker.characterName,
                                              attacker.corporationName,
                                              fb))
            lines.append("Damage Done: %s" % attacker.damageDone)
        else:
            lines.append("Name: %s%s" % (attacker.characterName, fb))
            lines.append("Security: %s" % attacker.securityStatus)
            lines.append("Corp: %s" % attacker.corporationName)
            if attacker.allianceID == 0:
                lines.append("Alliance: NONE")
            else:
                lines.append("Alliance: %s" % attacker.allianceName)
            if attacker.factionID == 0:
                lines.append("Faction: NONE")
            else:
                lines.append("Faction: %s" % attacker.factionName)
            lines.append("Ship: %s" % typeid2name(attacker.shipTypeID))
            lines.append("Weapon: %s" % typeid2name(attacker.weaponTypeID))
            lines.append("Damage Done: %s" % attacker.damageDone)
    destroyed = []
    dropped = []
    for item in getattr(kill, 'items', []):
        typename = typeid2name(item.typeID)
        if item.flag == 5:
            flag = " (Cargo)"
        elif item.flag == 87:
            flag = " (Drone Bay)"
        else:
            flag = ""
        if item.qtyDropped == 1:
            dropped.append("%s%s" % (typename, flag))
        elif item.qtyDropped > 1:
            dropped.append("%s, Qty: %s%s" % (typename, item.qtyDropped, flag))
        if item.qtyDestroyed == 1:
            destroyed.append("%s%s" % (typename, flag))
        elif item.qtyDestroyed > 1:
            destroyed.append("%s, Qty: %s%s" % (typename, item.qtyDestroyed,
                                                flag))
    if len(destroyed) > 0:
        lines.append("")
        lines.append("Destroyed items:")
        lines.append("")
        lines.extend(destroyed)
    if len(dropped) > 0:
        lines.append("")
        lines.append("Dropped items:")
        lines.append("")
        lines.extend(dropped)
    return "".join(line + "\n" for line in lines)

_typenames = None
def typeid2name(typeid):
    if typeid == 0:
        return "Unknown"
    global _typenames
    if _typenames is None:
        conn = db.connect()
        c = conn.cursor()
        c.execute("SELECT typeid, typename FROM ccp.invtypes")
        _typenames = dict(c.fetchall())
    return _typenames[typeid]

_sysnames = None
def systemid2name(sysid):
    global _sysnames
    if _sysnames is None:
        conn = db.connect()
        c = conn.cursor()
        c.execute("SELECT solarsystemid, solarsystemname "
                  "FROM ccp.mapsolarsystems")
        _sysnames = dict(c.fetchall())
    return _sysnames[sysid]

_syssec = None
def systemid2sec(sysid):
    global _syssec
    if _syssec is None:
        conn = db.connect()
        c = conn.cursor()
        c.execute("SELECT solarsystemid, security "
                  "FROM ccp.mapsolarsystems")
        _syssec = dict(c.fetchall())
    return _syssec[sysid]

_npccorps = None
def is_npc_corp(corpid):
    global _npccorps
    if _npccorps is None:
        conn = db.connect()
        c = conn.cursor()
        c.execute("SELECT corporationid FROM ccp.crpnpccorporations")
        _npccorps = set(x for (x,) in c.fetchall())
        c.execute("SELECT factionid FROM ccp.chrfactions")
        _npccorps.update(x for (x,) in c.fetchall())
    return corpid in _npccorps

# http://eve-kill.net/?a=idfeed&allkills=1&regionname=Heimatar
# http://eve-kill.net/?a=idfeed&allkills=1&regionname=Metropolis
# http://eve-kill.net/?a=idfeed&allkills=1&regionname=Molden+Heath
