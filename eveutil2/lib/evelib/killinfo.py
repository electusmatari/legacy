# EVE kill info parser

import evelib.newdb as db

import datetime
import re
import StringIO

class ParsingError(Exception):
    pass

ITEM_RX = re.compile(r'^(.*?)(?:, qty: ([0-9]*))?(?: \((cargo|drone bay)\))?$', re.I)

class KillInfo(object):
    def __init__(self, fileobj):
        self.timestamp = None
        self.victim = None
        self.involved = []
        self.items = {}
        self.read_sections(fileobj)
        if len(self.involved) == 0:
            raise RuntimeError("No involved parties!")

    def read_sections(self, fileobj):
        section = "timestamp"
        buf = []
        for line in fileobj:
            line = line.strip()
            if section == 'timestamp':
                if line != '':
                    self.timestamp = self.parse_timestamp(line)
                    section = 'victim'
            elif section == 'victim':
                if line.lower() == 'involved parties:':
                    self.victim = self.parse_victim("\n".join(buf))
                    buf = []
                    section = 'involved'
                else:
                    buf.append(line)
            elif section == 'involved':
                if line.lower() == 'destroyed items:':
                    self.involved = self.parse_involved("\n".join(buf))
                    buf = []
                    section = 'destroyed'
                elif line.lower() == 'dropped items:':
                    self.involved = self.parse_involved("\n".join(buf))
                    buf = []
                    section = 'dropped'
                else:
                    buf.append(line)
            elif section in ('destroyed', 'dropped'):
                if line.lower() == 'dropped items:':
                    section = 'dropped'
                elif line != '':
                    self.add_item(line, section)
        if section in ('timestamp', 'victim'):
            raise ParsingError("Malformed kill mail, ends prematurely")
        elif section == 'involved':
            self.involved = self.parse_involved("\n".join(buf))
        elif section in ('destroyed', 'dropped'):
            pass # Already handled

    def parse_timestamp(self, line):
        try:
            dt = datetime.datetime.strptime(line, "%Y.%m.%d %H:%M:%S")
        except ValueError:
            try:
                dt = datetime.datetime.strptime(line, "%Y.%m.%d %H:%M")
            except ValueError:
                dt = None
        return dt

    def parse_victim(self, data):
        victims = self.parse_blocks(data)
        if len(victims) != 1:
            raise ParsingError("Malformed kill mail, more than one victim")
        return fixblock(victims[0])

    def parse_involved(self, data):
        return [fixblock(block) for block in self.parse_blocks(data)]

    def add_item(self, line, type):
        m = ITEM_RX.match(line)
        if m is None:
            raise ParsingError("Malformed kill mail, item line bogus: %r" % line)
        (typename, qty, location) = m.groups()
        if qty is None:
            qty = 1
        else:
            qty = int(qty)
        if location is None:
            location = "fitted"
        self.items.setdefault(typename, {})
        self.items[typename].setdefault(location, 0)
        self.items[typename][location] += qty

    def parse_blocks(self, data):
        result = []
        block = {}
        for line in data.split("\n"):
            if line == '':
                if len(block) > 0:
                    result.append(block)
                    block = {}
            elif ":" not in line:
                raise ParsingError("No colon in line %r" % line)
            else:
                (name, value) = line.split(":", 1)
                if name in block:
                    raise ParsingError("Duplicate key %r in block" % name)
                block[name.strip()] = value.strip()
        if len(block) > 0:
            result.append(block)
        return result

def fixblock(block):
    if "Name" in block and block["Name"].endswith(" (laid the final blow)"):
        block["Final Blow"] = True
        block["Name"] = block["Name"][:-22]
    if "Name" in block and "/" in block["Name"]:
        (name, corp) = block["Name"].split("/", 1)
        block["Name"] = name.strip()
        block["Corp"] = corp.strip()
        block["NPC"] = True
    if "Faction" in block and block["Faction"].lower() in ('unknown', 'none'):
        block["Faction"] = None
    if "Alliance" in block and block["Alliance"].lower() in ('unknown', 'none'):
        block["Alliance"] = None
    if "Security" in block and "," in block["Security"]:
        block["Security"] = block["Security"].replace(",", ".")
    return block

# CREATE TABLE killinfo (
#     id SERIAL PRIMARY KEY,
#     date TIMESTAMP NOT NULL,
#     external_id INT DEFAULT NULL,
#     system_id INT NOT NULL REFERENCES ki_system(id),
#     moon_id INT REFERENCES ki_moon(id),
#     victim_id INT REFERENCES ki_pilot(id),
#     corp_id INT NOT NULL REFERENCES ki_corp(id),
#     alliance_id INT REFERENCES ki_alliance(id),
#     faction_id INT REFERENCES ki_faction(id),
#     destroyed_id INT REFERENCES ki_type(id),
#     damagetaken INT NOT NULL,
#     original TEXT NOT NULL,
#     source VARCHAR(255) NOT NULL,
#     UNIQUE (date, system_id, victim_id, destroyed_id)
# );
# 
# CREATE TABLE ki_involved (
#     id SERIAL PRIMARY KEY,
#     kill_id INT REFERENCES killinfo(id),
#     index INT NOT NULL,
#     name_id INT NOT NULL REFERENCES ki_pilot(id),
#     corp_id INT NOT NULL REFERENCES ki_corp(id),
#     alliance_id INT REFERENCES ki_alliance(id),
#     faction_id INT REFERENCES ki_faction(id),
#     security FLOAT,
#     isnpc BOOLEAN NOT NULL DEFAULT 'f',
#     isfinalblow BOOLEAN NOT NULL DEFAULT 'f',
#     ship_id INT REFERENCES ki_type(id),
#     damagedone INT NOT NULL,
#     weapon_id INT REFERENCES ki_type(id)
# );
#
# CREATE INDEX ki_involved_kill_id_idx ON ki_involved (kill_id);
# 
# CREATE TABLE ki_item (
#     id SERIAL PRIMARY KEY,
#     kill_id INT REFERENCES killinfo(id),
#     type_id INT NOT NULL REFERENCES ki_type(id),
#     location_id INT NOT NULL REFERENCES ki_itemlocation(id),
#     quantity INT NOT NULL
# );
#
# CREATE INDEX ki_item_kill_id_idx ON ki_item (kill_id);
#
# CREATE TABLE ki_faction (
#     id SERIAL PRIMARY KEY,
#     name VARCHAR(255) NOT NULL,
#     externalid INT NOT NULL
# );
# 
# CREATE TABLE ki_itemlocation (
#   id SERIAL PRIMARY KEY,
#   name VARCHAR(255) NOT NULL
# );
# 
# CREATE TABLE ki_moon (
#   id SERIAL PRIMARY KEY,
#   name VARCHAR(255) NOT NULL,
#   externalid INT
# );
# 
# CREATE TABLE ki_system (
#   id SERIAL PRIMARY KEY,
#   name VARCHAR(255) NOT NULL UNIQUE,
#   externalid INT
# );
# 
# CREATE TABLE ki_type (
#   id SERIAL PRIMARY KEY,
#   name VARCHAR(255) NOT NULL UNIQUE,
#   externalid INT
# );
# 
# CREATE TABLE ki_alliance (
#     id SERIAL PRIMARY KEY,
#     -- Kill mails
#     name VARCHAR(255) NOT NULL UNIQUE,
#     last_seen TIMESTAMP NOT NULL,
#     -- API
#     externalid INT,
#     is_closed BOOLEAN NOT NULL DEFAULT 'f',
#     last_api_check TIMESTAMP
# );
# 
# CREATE TABLE ki_corp (
#     id SERIAL PRIMARY KEY,
#     -- Killmails
#     name VARCHAR(255) NOT NULL UNIQUE,
#     alliance_id INT REFERENCES ki_alliance(id),
#     faction_id INT REFERENCES ki_faction(id),
#     last_seen TIMESTAMP NOT NULL,
#     -- API
#     externalid INT,
#     members INT,
#     is_closed BOOLEAN NOT NULL DEFAULT 'f',
#     last_api_check TIMESTAMP
# );
# 
# CREATE TABLE ki_pilot (
#     id SERIAL PRIMARY KEY,
#     -- Kill mails
#     name VARCHAR(255) NOT NULL UNIQUE,
#     corp_id INT NOT NULL REFERENCES ki_corp(id),
#     alliance_id INT REFERENCES ki_alliance(id),
#     faction_id INT REFERENCES ki_faction(id),
#     last_seen TIMESTAMP NOT NULL,
#     -- API
#     externalid INT,
#     is_dead BOOLEAN NOT NULL DEFAULT 'f',
#     last_api_check TIMESTAMP
# );


def add_killinfo(c, original, source):
    ki = KillInfo(StringIO.StringIO(original))
    killinfo_id = add_victim(c, ki, original, source)
    if killinfo_id is None:
        return False
    add_involved(killinfo_id, c, ki)
    add_items(killinfo_id, c, ki)
    return True

def add_victim(c, ki, original, source):
    system_id = get_system(c, ki.victim.get("System", None))
    moon_id = get_moon(c, ki.victim.get("Moon", None))
    faction_id = get_faction(c, ki.victim.get("Faction", None))
    alliance_id = get_alliance(c, ki.victim.get("Alliance", None),
                               ki.timestamp)
    corp_id = get_corp(c, ki.victim.get("Corp", None),
                       alliance_id, faction_id, ki.timestamp)
    victim_id = get_pilot(c, ki.victim.get("Victim", None),
                          corp_id, alliance_id, faction_id, ki.timestamp)
    destroyed_id = get_type(c, ki.victim["Destroyed"])
    c.execute("SELECT COUNT(*) FROM killinfo "
              "WHERE date = %s AND system_id = %s AND victim_id = %s "
              "  AND destroyed_id = %s",
              (ki.timestamp, system_id, victim_id, destroyed_id))
    if c.fetchone()[0] > 0:
        return None
    c.execute("INSERT INTO killinfo (date, system_id, moon_id, "
              "                      victim_id, corp_id, "
              "                      alliance_id, faction_id, destroyed_id, "
              "                      damagetaken, original, source) "
              "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
              "RETURNING id",
              (ki.timestamp,
               system_id,
               moon_id,
               victim_id,
               corp_id,
               alliance_id,
               faction_id,
               destroyed_id,
               ki.victim["Damage Taken"],
               original,
               source
              ))
    return c.fetchone()[0]

def add_involved(killinfo_id, c, ki):
    for idx, inv in enumerate(ki.involved):
        faction_id = get_faction(c, inv.get("Faction", None))
        alliance_id = get_alliance(c, inv.get("Alliance", None), ki.timestamp)
        corp_id = get_corp(c, inv.get("Corp", None),
                           alliance_id, faction_id, ki.timestamp)
        pilot_id = get_pilot(c, inv.get("Name", None),
                             corp_id, alliance_id, faction_id, ki.timestamp)
        c.execute("INSERT INTO ki_involved (kill_id, index, name_id, "
                  "                         corp_id, alliance_id, faction_id, "
                  "                         security, isnpc, isfinalblow, "
                  "                         ship_id, damagedone, weapon_id) "
                  "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ",
                  (killinfo_id,
                   idx,
                   pilot_id,
                   corp_id,
                   alliance_id,
                   faction_id,
                   inv.get("Security", 0.0),
                   inv.get("NPC", False),
                   inv.get("Final-Blow", False),
                   get_type(c, inv.get("Ship", None)),
                   inv["Damage Done"],
                   get_type(c, inv.get("Weapon", None))))

def add_items(killinfo_id, c, ki):
    for typename in ki.items:
        for location, qty in ki.items[typename].items():
            try:
                c.execute("INSERT INTO ki_item (kill_id, type_id, location_id, "
                          "                     quantity) "
                          "VALUES (%s, %s, %s, %s)",
                          (killinfo_id,
                           get_type(c, typename),
                           get_location(c, location),
                           qty))
            except:
                print "Values:", killinfo_id, get_type(c, typename), get_location(c, location), qty
                raise

def update_killinfo(c, killid):
    c.execute("SELECT original, source FROM killinfo WHERE id = %s",
              (killid,))
    if c.rowcount == 0:
        raise RuntimeError("Kill %s does not exist" % killid)
    (original, source) = c.fetchone()
    ki = KillInfo(StringIO.StringIO(original))
    c.execute("ALTER TABLE ki_involved DROP CONSTRAINT "
              "ki_involved_kill_id_fkey")
    c.execute("DELETE FROM ki_involved WHERE kill_id = %s",
              (killid,))
    c.execute("ALTER TABLE ki_involved ADD CONSTRAINT "
              "ki_involved_kill_id_fkey "
              "FOREIGN KEY (kill_id) REFERENCES killinfo (id)")

    c.execute("ALTER TABLE ki_item DROP CONSTRAINT "
              "ki_item_kill_id_fkey")
    c.execute("DELETE FROM ki_item WHERE kill_id = %s",
              (killid,))
    c.execute("ALTER TABLE ki_item ADD CONSTRAINT "
              "ki_item_kill_id_fkey "
              "FOREIGN KEY (kill_id) REFERENCES killinfo (id)")

    faction_id = get_faction(c, ki.victim.get("Faction", None))
    alliance_id = get_alliance(c, ki.victim.get("Alliance", None),
                               ki.timestamp)
    corp_id = get_corp(c, ki.victim["Corp"], alliance_id, faction_id,
                       ki.timestamp)
    pilot_id = get_pilot(c, ki.victim.get("Victim", None),
                         corp_id, alliance_id, faction_id,
                         ki.timestamp)

    c.execute("UPDATE killinfo "
              "   SET date = %s, "
              "       system_id = %s, "
              "       moon_id = %s, " 
              "       victim_id = %s, "
              "       corp_id = %s, "
              "       alliance_id = %s, "
              "       faction_id = %s, "
              "       destroyed_id = %s, "
              "       damagetaken = %s "
              "WHERE id = %s",
              (ki.timestamp,
               get_system(c, ki.victim.get("System", None)),
               get_moon(c, ki.victim.get("Moon", None)),
               pilot_id,
               corp_id,
               alliance_id,
               faction_id,
               get_type(c, ki.victim["Destroyed"]),
               ki.victim["Damage Taken"],
               killid
              ))
    add_involved(killid, c, ki)
    add_items(killid, c, ki)

def get_location(c, name):
    if name is None:
        return None
    return get_or_create(c, ["id"], "ki_itemlocation", {'name': name})[0]

def get_type(c, name):
    if name is None:
        return None
    return get_or_create(c, ["id"], "ki_type", {'name': name})[0]

def get_system(c, name):
    if name is None:
        return None
    return get_or_create(c, ["id"], "ki_system", {'name': name})[0]

def get_moon(c, name):
    if name is None:
        return None
    return get_or_create(c, ["id"], "ki_moon", {'name': name})[0]

def get_faction(c, name):
    if name is None:
        return None
    return get_or_create(c, ["id"], "ki_faction", {'name': name})[0]

def get_alliance(c, name, timestamp):
    if name is None:
        return None
    (alliance_id, last_seen) = get_or_create(c, ["id", "last_seen"], 
                                             "ki_alliance",
                                             {'name': name},
                                             {'last_seen': timestamp})
    if last_seen < timestamp:
        c.execute("UPDATE ki_alliance SET last_seen = %s "
                  "WHERE id = %s",
                  (timestamp, alliance_id))
    return alliance_id

def get_corp(c, name, alliance_id, faction_id, timestamp):
    if name is None:
        return None
    (corp_id, last_seen) = get_or_create(c, ["id", "last_seen"], 
                                         "ki_corp",
                                         {'name': name},
                                         {'last_seen': timestamp,
                                          'alliance_id': alliance_id,
                                          'faction_id': faction_id})
    if last_seen < timestamp:
        c.execute("UPDATE ki_corp "
                  "SET last_seen = %s, "
                  "    alliance_id = %s, "
                  "    faction_id = %s "
                  "WHERE id = %s",
                  (timestamp, alliance_id, faction_id, corp_id))
    return corp_id
    
def get_pilot(c, name, corp_id, alliance_id, faction_id, timestamp):
    if name is None:
        return None
    (pilot_id, last_seen) = get_or_create(c, ["id", "last_seen"], 
                                          "ki_pilot",
                                          {'name': name},
                                          {'last_seen': timestamp,
                                           'corp_id': corp_id,
                                           'alliance_id': alliance_id,
                                           'faction_id': faction_id})
    if last_seen < timestamp:
        c.execute("UPDATE ki_pilot "
                  "SET last_seen = %s, "
                  "    corp_id = %s, "
                  "    alliance_id = %s, "
                  "    faction_id = %s "
                  "WHERE id = %s",
                  (timestamp, corp_id, alliance_id, faction_id, pilot_id))
    return pilot_id

def get_or_create(c, columns, table, where, defaults={}):
    """
    Return COLUMNS from TABLE where the row matches WHERE.

    If no such column exists, create one with the values in DEFAULTS.
    """
    def select():
        c.execute("SELECT %s FROM %s WHERE %s FOR UPDATE" %
                  (", ".join(["%s"] * len(columns)),
                   "%s",
                   " AND ".join(["%s = %s"] * len(where))),
                  tuple([db.PGName(col) for col in columns] +
                        [db.PGName(table)] +
                        flatten([(db.PGName(col), val)
                                 for (col, val) in where.items()])))
        if c.rowcount > 1:
            raise RuntimeError("More than one row found in %s for %r" %
                               (table, where))
        elif c.rowcount == 1:
            return c.fetchone()
        else:
            return None
    row = select()
    if row is not None:
        return row
    c.execute("LOCK TABLE %s IN EXCLUSIVE MODE",
              (db.PGName(table),))
    row = select()
    if row is not None:
        return row
    data = where.items() + defaults.items()
    c.execute("INSERT INTO %s (%s) VALUES (%s) RETURNING %s" %
              ("%s",
               ", ".join(["%s"] * len(data)),
               ", ".join(["%s"] * len(data)),
               ", ".join(["%s"] * len(columns))),
              tuple([db.PGName(table)] +
                    [db.PGName(col) for (col, val) in data] +
                    [val for (col, val) in data] +
                    [db.PGName(col) for col in columns]))
    return c.fetchone()

def flatten(lis):
    """
    Return a list of concatenated sublists.
    """
    result = []
    for elt in lis:
        result.extend(elt)
    return result
