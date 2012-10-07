#!/usr/bin/env python

import re
import sys

import evelib.api as api

def main():
    headline_rx = re.compile(r'^\* ([^(]*)(?: \(.*\))?$')
    entity_rx = re.compile(r'^- ([^<[]*)(?: ([<[].*[]>]))?(?: \(.*\))?$')
    last_headline = None
    output = []
    totalsize = 0
    for line in sys.stdin:
        line = line.strip()
        headline_match = headline_rx.match(line)
        entity_match = entity_rx.match(line)
        if headline_match is not None:
            if last_headline is not None:
                sys.stdout.write("* %s (%s)\n" % (last_headline, totalsize))
                sys.stdout.write("\n".join(output))
                sys.stdout.write("\n")
            last_headline = headline_match.group(1)
            facwar = get_faction(last_headline)
            output = []
            totalsize = 0
            if facwar is not None:
                sys.stdout.write("* %s (%s)\n" % (last_headline, facwar))
                last_headline = None
        elif entity_match is not None:
            name = entity_match.group(1)
            info = get_info(name)
            if info is None:
                output.append(line)
            else:
                (name, ticker, size) = info
                output.append("- %s %s (%s)" % (name, ticker, size))
                totalsize += size
        elif last_headline is not None:
            output.append(line)
        else:
            sys.stdout.write(line)
            sys.stdout.write("\n")
    if last_headline is not None:
        sys.stdout.write("* %s (%s)\n" % (last_headline, totalsize))
        sys.stdout.write("\n".join(output))
        sys.stdout.write("\n")

_alliances = None
def get_info(name):
    apiroot = api.api()
    global _alliances
    if _alliances is None:
        _alliances = {}
        for alliance in apiroot.eve.AllianceList().alliances:
            _alliances[alliance.name.lower()] = (alliance.name,
                                                 "<%s>" % alliance.shortName,
                                                 alliance.memberCount)
    result = _alliances.get(name.lower(), None)
    if result is not None:
        return result
    try:
        corpid = apiroot.eve.CharacterID(names=name).characters[0].characterID
        sheet = apiroot.corp.CorporationSheet(corporationID=corpid)
        return sheet.corporationName, "[%s]" % sheet.ticker, sheet.memberCount
    except:
        return None

_factions = None
def get_faction(name):
    apiroot = api.api()
    global _factions
    if _factions is None:
        _factions = {}
        for faction in apiroot.eve.FacWarStats().factions:
            facname = "%s Militia" % faction.factionName.split(" ")[0]
            _factions[facname] = faction.pilots
    return _factions.get(name, None)

main()
