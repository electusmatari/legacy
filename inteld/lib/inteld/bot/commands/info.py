from django.db import connection

from emtools.ccpeve.models import apiroot
from inteld.utils import get_standings

def info_npccorp(itemid):
    c = connection.cursor()
    c.execute("SELECT cn.itemname, fn.itemname "
              "FROM ccp.crpnpccorporations c "
              "     INNER JOIN ccp.invnames cn ON c.corporationid = cn.itemid "
              "     INNER JOIN ccp.invnames fn ON c.factionid = fn.itemid "
              "WHERE c.corporationid = %s",
              (itemid,))
    if c.rowcount < 1:
        return None
    else:
        corpname, factionname = c.fetchone()
        return {'name': corpname,
                'faction': factionname}

def info_solarsystem(itemid):
    c = connection.cursor()
    c.execute("""
SELECT s.solarsystemname, r.regionname, s.security,
       fw.owningfactionname,
       fw.occupyingfactionname, fw.victorypoints
FROM ccp.mapsolarsystems s
     INNER JOIN ccp.mapconstellations c
       ON s.constellationid = c.constellationid
     INNER JOIN ccp.mapregions r
       ON c.regionid = r.regionid
     LEFT JOIN uploader_facwarsystem fw
       ON s.solarsystemid = fw.solarsystemid
WHERE s.solarsystemid = %s
""", (itemid,))
    if c.rowcount < 1:
        return None
    name, region, security, faction, occupier, vp = c.fetchone()
    result = {'name': name,
              'region': region,
              'security': security,
              'faction': faction}
    if occupier is not None and occupier != faction:
        result['occupied'] = occupier
    if vp is not None:
        result['vp'] = vp
    api = apiroot()
    try:
        kills = api.map.Kills()
    except:
        pass
    else:
        for sys in kills.solarSystems:
            if sys.solarSystemID == itemid:
                result['kills'] = sys.shipKills
                result['podkills'] = sys.podKills
                result['npckills'] = sys.factionKills
                break
    return result

def info_apialliance(ownerid):
    api = apiroot()
    standings = get_standings()
    for ally in api.eve.AllianceList().alliances:
        if ally.allianceID == ownerid:
            return {'name': ally.name,
                    'ticker': ally.shortName,
                    'size': ally.memberCount,
                    'standing': standings.get(ally.allianceID, 0)}
    return None

def info_apicorp(ownerid):
    api = apiroot()
    try:
        cs = api.corp.CorporationSheet(corporationID=ownerid)
    except:
        return None
    result = {'name': cs.corporationName,
              'ticker': cs.ticker,
              'hq': cs.stationName,
              'alliance': getattr(cs, 'allianceName', None),
              'size': cs.memberCount}
    c = connection.cursor()
    c.execute("SELECT f.name "
              "FROM intel_corporation c "
              "     INNER JOIN intel_faction f "
              "       ON c.faction_id = f.id "
              "WHERE c.corporationid = %s",
              (ownerid,))
    result['faction'] = None
    if c.rowcount > 0:
        (faction,) = c.fetchone()
        result['faction'] = faction
    standings = get_standings()
    result['standing'] = standings.get(ownerid, 0)
    result['alliancestanding'] = standings.get(getattr(cs, 'allianceID', 
                                                       None), 0)
    return result

def info_apichar(ownerid):
    api = apiroot()
    try:
        charinfo = api.eve.CharacterInfo(characterID=ownerid)
    except:
        return None
    c = connection.cursor()
    c.execute("SELECT f.name "
              "FROM intel_corporation c "
              "     INNER JOIN intel_faction f "
              "       ON c.faction_id = f.id "
              "WHERE c.corporationid = %s",
              (charinfo.corporationID,))
    if c.rowcount > 0:
        (faction,) = c.fetchone()
    else:
        faction = None
    result = {'name': charinfo.characterName,
              'security': charinfo.securityStatus,
              'corp': charinfo.corporation,
              'race': charinfo.race,
              'bloodline': charinfo.bloodline,
              'alliance': getattr(charinfo, 'alliance', None),
              'corpfaction': faction}
    standings = get_standings()
    result['corpstanding'] = standings.get(charinfo.corporationID, 0)
    result['alliancestanding'] = standings.get(getattr(charinfo,
                                                       'allianceID', None),
                                               0)
    return result
