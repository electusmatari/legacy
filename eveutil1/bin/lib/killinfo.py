# Kill info file parser

import datetime
import re

class KillInfoParseException(Exception):
    pass

class KillInfo(object):
    def __init__(self):
        self.timestamp = None
        self.victim = {}
        self.involved = []
        self.items = {}

def load(file):
    """Load a KillInfo object from a file object."""
    ki = KillInfo()
    lines = [line.rstrip() for line in file]
    lines = load_date(ki, lines)
    lines = load_section(ki, lines, section='Victim')
    while len(lines) > 0:
        lines = load_section(ki, lines)
    if ki.victim["Alliance"].lower() == "keine":
        ki.victim["Alliance"] = "None"
    for inv in ki.involved:
        if inv.get("Alliance", "").lower() == "keine":
            inv["Alliance"] = "None"
    return ki

def load_date(ki, lines):
    """A kill info starts with a date line and then a blank line.
    Return unparsed lines.
    """
    lines = drop_empty(lines)
    if len(lines) == 0:
        raise KillInfoParseException("Truncated kill info: No date line")
    if lines[0].count(":") > 1:
        lines[0] = lines[0][:-3]
    ki.timestamp = datetime.datetime.strptime(lines[0], "%Y.%m.%d %H:%M")
    return drop_empty(lines[1:])

def load_section(ki, lines, section=None):
    """Load a section from the kill info."""
    lines = drop_empty(lines)
    if not section:
        if len(lines) == 0:
            raise KillInfoParseException('Truncated kill info')
        if lines[0][-1] != ':':
            raise KillInfoParseException('Malformed kill info: No section name')
        section = lines[0][:-1]
        lines = drop_empty(lines[1:])
    if section == 'Victim':
        lines = parse_rfc822(ki.victim, lines)
    elif section == 'Involved parties':
        lines = parse_involved(ki.involved, lines)
    elif section == 'Destroyed items':
        lines = parse_items(ki.items, lines, destroyed=True)
    elif section == 'Dropped items':
        lines = parse_items(ki.items, lines, destroyed=False)
    elif section == 'Name':
        # Malformed involved parties section
        lines = parse_involved(ki.involved, ['Name: Unknown'] + lines)
    else:
        raise KillInfoParseException("Malformed kill info: Unknown section '%s'",
                                     section)
    return drop_empty(lines)

def parse_involved(involved, lines):
    """Parse multiple blocks of involved parties."""
    lines = drop_empty(lines)
    while len(lines) > 0 and lines[0][-1] != ':':
        data = {}
        lines = parse_rfc822(data, lines)
        fix_involved(data)
        involved.append(data)
    return drop_empty(lines)

def fix_involved(data):
    """Fix involved parties.
    Fixes NPC kill entry and the final blow statement.
    """
    if "Name" not in data:
        return data

    if data["Name"].endswith(" (laid the final blow)"):
        data["Name"] = data["Name"][:-22]
        data["Final Blow"] = True
    else:
        data["Final Blow"] = False

    if "/" in data["Name"]:
        (data["Name"], data["Corp"]) = data["Name"].split("/", 1)
        data["Name"] = data["Name"].strip()
        data["Corp"] = data["Corp"].strip()
        data['Capsuleer'] = False
    else:
        data['Capsuleer'] = True

    return data

def parse_items(items, lines, destroyed):
    """Parse a bunch of items."""
    lines = drop_empty(lines)
    while len(lines) > 0 and lines[0] != '':
        (line, lines) = (lines[0], lines[1:])
        if " (" in line:
            start = line.rindex(" (")
            location = line[start+2:-1]
            line = line[:start]
        else:
            location = "Fitted"
        if ", Qty: " in line:
            start = line.rindex(", Qty: ")
            qty = int(line[start+7:])
            line = line[:start]
        else:
            qty = 1

        if location not in items:
            items[location] = {}
        if line in items[location]:
            (qty_destroyed, qty_dropped) = items[location][line]
        else:
            (qty_destroyed, qty_dropped) = (0, 0)
        if destroyed:
            qty_destroyed += qty
        else:
            qty_dropped += qty
        items[location][line] = (qty_destroyed, qty_dropped)
    return drop_empty(lines)

def parse_rfc822(data, lines):
    """Parse a 822 header block.
    Return the remaining lines after the first empty line.
    """
    while len(lines) > 0 and lines[0] != '':
        (line, lines) = (lines[0], lines[1:])
        try:
            colon = line.index(":")
        except ValueError:
            raise KillInfoParseException('Malformed kill info: No colon in a block line?')
        data[line[:colon].strip()] = line[colon+2:].strip()
    return drop_empty(lines)

def drop_empty(lines):
    """Drop empty lines from the list."""
    while len(lines) > 0 and lines[0] == '':
        lines = lines[1:]
    return lines
