# coding: utf-8

from emtools.ccpeve.ccpdb import get_moonid

import datetime

class Killinfo(object):
    def __init__(self):
        self.killid = None
        self.kill_internal_id = None
        self.solarsystemid = None
        self.killtime = None
        self.moonid = None
        # Victim
        self.victim = Victim()
        self.damagetaken = None
        self.shiptypeid = None
        # Attackers
        self.attackers = []
        # Items
        self.items = []

    def fix(self):
        self.fix_ccp_idiocies()
        self.fix_edk_idiocies()

    def fix_ccp_idiocies(self):
        for p in [self.victim] + self.attackers:
            if p.alliancename.lower() in ['Неизвестно', u'неизвестно',
                                          'неизвестно', 'het', 'unbekannt',
                                          'keine', 'unknown', 'none']:
                p.alliancename = None
                p.allianceid = None

    def fix_edk_idiocies(self):
        if '- Moon ' in self.victim.charactername:
            self.victim.moonid = get_moonid(self.victim.charactername.strip())
            self.victim.characterid = None
            self.victim.charactername = None
        factions = {'amarr empire': (500003, 'Amarr Empire'),
                    'minmatar republic': (500002, 'Minmatar Republic'),
                    'gallente federation': (500004, 'Gallente Federation'),
                    'caldari state': (500001, 'Caldari State')
                    }
        for p in [self.victim] + self.attackers:
            if p.allianceName.lower() in factions:
                p.factionid, p.factionname = factions[p.allianceName.lower()]
                p.alliancename = None
                p.allianceid = None
            if " - " in p.charactername: # NPC
                p.charactername = ''
                p.characterid = 0
            if p.characterid < 500000: # typeID is not a characterID, ffs
                p.characterid = 0
                p.charactername = ''


class Person(object):
    def __init__(self, characterid=None, charactername=None,
                 corporationid=None, corporationname=None,
                 allianceid=None, alliancename=None,
                 factionid=None, factionname=None):
        self.characterid = characterid
        self.charactername = charactername
        self.corporationid = corporationid
        self.corporationname = corporationname
        self.allianceid = allianceid
        self.alliancename = alliancename
        self.factionid = factionid
        self.factionname = factionname

class Victim(Person):
    def __init__(self, damagetaken=None, shiptypeid=None, **kwargs):
        super(Victim, self).__init__(**kwargs)
        self.damagetaken = damagetaken
        self.shiptypeid = shiptypeid

class Attacker(Person):
    def __init__(self, security=None, damagedone=None, finalblow=None,
                 weapontypeid=None, shiptypeid=None, **kwargs):
        super(Attacker, self).__init__(**kwargs)
        self.security = security
        self.damagedone = damagedone
        self.finalblow = finalblow
        self.weapontypeid = weapontypeid
        self.shiptypeid = shiptypeid

class Item(object):
    def __init__(self, typeid=None, typename=None, flag=None,
                 location=None, qtydropped=None, qtydestroyed=None):
        self.typeid = typeid
        self.typename = typename
        self.flag = flag
        self.location = location
        self.qtydropped = qtydropped
        self.qtydestroyed = None

def strn(obj):
    if obj is None or obj == '':
        return None
    if not isinstance(obj, basestring):
        obj = str(obj)
    try:
        return unicode(obj)
    except UnicodeDecodeError:
        pass
    try:
        return obj.decode("utf-8")
    except UnicodeDecodeError:
        return obj.decode("latin-1")

def intn(obj):
    if obj is None or obj == '':
        return None
    else:
        return int(obj)

from xml.etree import ElementTree

def parse_api_page(xml):
    tree = ElementTree.fromstring(xml)
    result = []
    for row in tree.findall("result/rowset/row"):
        ki = Killinfo()
        ki.killid = intn(row.get('killID'))
        ki.kill_internal_id = intn(row.get('killInternalID'))
        if ki.kill_internal_id is None:
            ki.kill_internal_id = ki.killid
            ki.killid = None
        ki.solarsystemid = intn(row.get('solarSystemID'))
        ki.killtime = datetime.datetime.strptime(row.get('killTime'),
                                                 "%Y-%m-%d %H:%M:%S")
        ki.moonid = intn(row.get('moonID'))

        victim = row.find("victim")
        ki.victim.characterid = intn(victim.get('characterID'))
        ki.victim.charactername = strn(victim.get('characterName'))
        ki.victim.corporationid = intn(victim.get('corporationID'))
        ki.victim.corporationname = strn(victim.get('corporationName'))
        ki.victim.allianceid = intn(victim.get('allianceID'))
        ki.victim.alliancename = strn(victim.get('allianceName'))
        ki.victim.factionid = intn(victim.get('factionID'))
        ki.victim.factionname = strn(victim.get('factionName'))
        ki.victim.damagetaken = intn(victim.get('damageTaken'))
        ki.victim.shiptypeid = intn(victim.get('shipTypeID'))

        def find_rows(tree, name):
            for rowset in tree.findall("rowset"):
                if rowset.get('name') == name:
                    return rowset.findall("row")
            return []

        for attacker in find_rows(row, 'attackers'):
            att = Attacker()
            att.characterid = intn(attacker.get('characterID'))
            att.charactername = strn(attacker.get('characterName'))
            att.corporationid = intn(attacker.get('corporationID'))
            att.corporationname = strn(attacker.get('corporationName'))
            att.allianceid = intn(attacker.get('allianceID'))
            att.alliancename = strn(attacker.get('allianceName'))
            att.security = attacker.get('securityStatus')
            att.damagedone = intn(attacker.get('damageDone'))
            att.finalblow = bool(attacker.get('finalBlow'))
            att.weapontypeid = intn(attacker.get('weaponTypeID'))
            att.shiptypeid = intn(attacker.get('shipTypeID'))
            ki.attackers.append(att)
        for item in find_rows(row, 'items'):
            i = Item()
            i.typeid = intn(item.get('typeID'))
            i.flag = intn(item.get('flag'))
            i.qtydropped = intn(item.get('qtyDropped'))
            i.qtydestroyed = intn(item.get('qtyDestroyed'))
            ki.items.append(i)
        result.append(ki)
    return result

def parse_eveapiinfo(kill):
    ki = Killinfo()
    ki.killid = intn(kill.killID)
    ki.kill_internal_id = intn(getattr(kill, 'killInternalID', None))
    if ki.kill_internal_id is None:
        ki.kill_internal_id = ki.killid
        ki.killid = None
    ki.solarsystemid = intn(kill.solarSystemID)
    ki.killtime = datetime.datetime.utcfromtimestamp(kill.killTime)
    ki.moonid = intn(kill.moonID)
    ki.victim.characterid = intn(kill.victim.characterID)
    ki.victim.charactername = strn(kill.victim.characterName)
    ki.victim.corporationid = intn(kill.victim.corporationID)
    ki.victim.corporationname = strn(kill.victim.corporationName)
    ki.victim.allianceid = intn(kill.victim.allianceID)
    ki.victim.alliancename = strn(kill.victim.allianceName)
    ki.victim.factionid = intn(kill.victim.factionID)
    ki.victim.factionname = strn(getattr(kill.victim, 'factionName', None))
    for attacker in kill.attackers:
        att = Attacker()
        att.characterid = intn(attacker.characterID)
        att.charactername = strn(attacker.characterName)
        att.corporationid = intn(attacker.corporationID)
        att.corporationname = strn(attacker.corporationName)
        att.allianceid = intn(attacker.allianceID)
        att.alliancename = strn(attacker.allianceName)
        att.security = attacker.securityStatus
        att.damagedone = intn(attacker.damageDone)
        att.finalblow = bool(attacker.finalBlow)
        att.weapontypeid = intn(attacker.weaponTypeID)
        att.shiptypeid = intn(attacker.shipTypeID)
        ki.attackers.append(att)
    if hasattr(kill, 'items'):
        for item in kill.items:
            i = Item()
            i.typeid = intn(item.typeID)
            i.flag = intn(item.flag)
            i.qtydropped = intn(item.qtyDropped)
            i.qtydestroyed = intn(item.qtyDestroyed)
            ki.items.append(item)
    return ki

def parse_textinfo(text):
    raise RuntimeError('parse_textinfo() not implemented yet')

