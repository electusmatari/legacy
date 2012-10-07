#!/usr/bin/env python

import cgitb; cgitb.enable()

import cgi
import csv
import os
import cPickle as pickle
import urllib

csvfile = "/home/forcer/Projects/old-emcom/ftp/data/grd-deliveries.csv"
picklefile = "/home/forcer/Projects/old-emcom/ftp/data/systems.pickle"

IS_IGB = False
sys_sec = {}
sys_jumps = {}

def main():
    print "Content-Type: text/html"
    print
    form = cgi.FieldStorage()

    global sys_sec
    global sys_jumps
    (sys_sec, sys_jumps) = pickle.load(file(picklefile))
    global IS_IGB
    if os.getenv("HTTP_USER_AGENT") and "EVE-minibrowser" in os.getenv("HTTP_USER_AGENT"):
        IS_IGB = True

    systems = get_deliveries(form.getfirst("system", "Pator"),
                             form.getfirst("type", False))
    systems = delivery_filter(form, systems)
    systems = delivery_sort(form, systems)

    emit_page(form, systems)

def delivery_filter(form, systems):
    safe = form.getfirst("safe")
    try:
        maxjumps = int(form.getfirst("maxjumps"))
    except:
        maxjumps = None
    try:
        minvol = int(form.getfirst("minvol"))
    except:
        minvol = None
    try:
        maxvol = int(form.getfirst("maxvol"))
    except:
        maxvol = None
    result = []
    for sys in systems:
        if safe and sys.sec < 0.45:
            continue
        if maxjumps and sys.jumps > maxjumps:
            continue
        if minvol and sys.vol < minvol:
            continue
        if maxvol and sys.vol > maxvol:
            continue
        result.append(sys)
    return result

def delivery_sort(form, systems):
    sortby = form.getfirst("sort", "")
    if sortby == "volume":
        systems.sort(lambda a, b: cmp((b.vol, a.sysname),
                                      (a.vol, b.sysname)))
    elif sortby == "jumps":
        systems.sort(lambda a, b: cmp((a.jumps, a.sysname),
                                      (b.jumps, b.sysname)))
    else:
        systems.sort(lambda a, b: cmp(a.sysname, b.sysname))
    return systems

def emit_page(form, systems):
    if form.getfirst("safe", False):
        safe = "checked"
    else:
        safe = ""

    if IS_IGB:
        style = css_igb
    else:
        style = css_external

    if form.getfirst("expandall", False) == "all":
        expandall = selflink(form, "expandall", "")
        symbol = "&#x25B2;"
    else:
        expandall = selflink(form, "expandall", "all")
        symbol = "&#x25BC;"

    print(html_page_header % 
          {"script": cgi.escape(os.getenv("SCRIPT_NAME")),
           "system": cgi.escape(form.getfirst("system", "Pator")),
           "type": cgi.escape(form.getfirst("type", "")),
           "minvol": cgi.escape(form.getfirst("minvol", "")),
           "maxvol": cgi.escape(form.getfirst("maxvol", "")),
           "safe": safe,
           "maxjumps": cgi.escape(form.getfirst("maxjumps", "")),
           "sortlocation": selflink(form, "sort", "location"),
           "sortvolume": selflink(form, "sort", "volume"),
           "sortjumps": selflink(form, "sort", "jumps"),
           "style": style,
           "expandall": expandall,
           "symbol": symbol,
           "stats": stats(systems)
           })
    expandall = form.getfirst("expandall", False) == "all"
    expandsystem = form.getfirst("expandsystem", False)
    expandstation = form.getfirst("expandstation", False)
    for sys in systems:
        if sys.sec <= 0.0:
            jumps = '<span class="nullsec">%s</span>' % sys.jumps
        elif sys.sec <  0.45:
            jumps = '<span class="lowsec">%s</span>' % sys.jumps
        else:
            jumps = '<span class="highsec">%s</span>' % sys.jumps
        if expandall or expandsystem == sys.sysname:
            syssymbol = "&#x25B2;"
            expandsystemlink = selflink(form, "expandsystem", "",
                                        anchor=cgi.escape(sys.sysname))
        else:
            syssymbol = "&#x25BC;"
            expandsystemlink = selflink(form, "expandsystem", sys.sysname,
                                        anchor=cgi.escape(sys.sysname))
        if expandall:
            syssymbol = ""
        if sys.buying:
            sysbuying = '<span class="yes">Yes</span>'
        else:
            sysbuying = '<span class="no">No</span>'
        print(html_system_row %
              {"showinfo": sys.showinfo(),
               "name": cgi.escape(sys.sysname),
               "volume": humane(sys.vol),
               "jumps": jumps,
               "expand": expandsystemlink,
               "buying": sysbuying,
               "symbol": syssymbol})
        if expandall or expandsystem == sys.sysname:
            sys.stations.sort(lambda a, b: cmp(a.staname, b.staname))
            for sta in sys.stations:
                if expandall or expandstation == sta.staname:
                    stasymbol = "&#x25B2;"
                    expandstationlink = selflink(form, "expandstation", "",
                                                 anchor=cgi.escape(sys.sysname))
                else:
                    stasymbol = "&#x25BC;"
                    expandstationlink = selflink(form, "expandstation", sta.staname,
                                                 anchor=cgi.escape(sys.sysname))
                if expandall:
                    stasymbol = ""
                if sta.buying:
                    stabuying = '<span class="yes">Yes</span>'
                else:
                    stabuying = '<span class="no">No</span>'
                print(html_station_row %
                      {"showinfo": sta.showinfo(),
                       "volume": humane(sta.vol),
                       "expand": expandstationlink,
                       "buying": stabuying,
                       "symbol": stasymbol})
                if expandall or expandstation == sta.staname:
                    sta.piles.sort(lambda a, b: cmp(a.typename, b.typename))
                    for pile in sta.piles:
                        if pile.buying:
                            pilebuying = '<span class="yes">Yes</span>'
                        else:
                            pilebuying = '<span class="no">No</span>'
                        print(html_pile_row %
                              {"showinfo": pile.showinfo(),
                               "qty": humane(pile.qty),
                               "volume": humane(pile.vol),
                               "buying": pilebuying})
    print(html_page_footer)

def selflink(form, name=None, value=None, anchor=None):
    """
    Return a link to this script, but set the option name to value.
    """
    l = [(x.name, x.value) for x in form.list if x.name != name]
    l.append((name, value))
    url = cgi.escape(os.getenv("SCRIPT_NAME")) + "?" + urllib.urlencode(l)
    if anchor:
        url += "#" + cgi.escape(anchor)
    return url

def get_deliveries(current_system, typefilter):
    rows = list(csv.reader(file(csvfile)))
    systems = {}
    stations = {}

    for (sysname, sysid, staname, staid, statypeid, 
         typename, typeid, qty, vol,
         system_buying, item_buying) in rows:
        if typefilter and typefilter.lower() not in typename.lower():
            continue
        vol = float(vol)
        qty = int(qty)
        system_buying = (system_buying == "True")
        item_buying = (item_buying == "True")
        if sysname not in systems:
            systems[sysname] = System(sysname, sysid,
                                      distance(sysname, current_system),
                                      sec(sysname),
                                      system_buying)
        if staname not in stations:
            stations[staname] = Station(staname, staid, statypeid)
            systems[sysname].add_station(stations[staname])
        stations[staname].add_pile(Pile(typename, typeid, qty, vol,
                                        item_buying))
    for sys in systems.values():
        sys.recalc()
    return systems.values()

def stats(systems):
    nsys = 0
    nstas = 0
    total_vol = 0
    for sys in systems:
        nsys += 1
        for sta in sys.stations:
            nstas += 1
            for pile in sta.piles:
                total_vol += pile.vol
    return("%s m3 in %s systems and %s stations." %
           (humane(total_vol), nsys, nstas))

def distance(a, b):
    if a not in sys_jumps or b not in sys_jumps:
        return 0
    return find_distance(a, b, sys_jumps)

def sec(sysname):
    if sysname in sys_sec:
        return sys_sec[sysname]
    else:
        return 1.0

def escape(s):
    return cgi.escape(s).replace(" ", "&nbsp;")

def humane(num):
    if num < 0:
        sign = "-"
        num *= -1
    else:
        sign = ""
    if type(num) == float:
        s = "%.2f" % num
        prefix = s[:-3]
        result = s[-3:]
    else:
        s = "%i" % num
        prefix = s
        result = ""

    i = 0
    while len(prefix) > 3:
        result = "," + prefix[-3:] + result
        prefix = prefix[:-3]
    return sign + prefix + result

def find_distance(start, end, neighbors):
    visited = {}
    agenda = [(start, 0)]
    while len(agenda) > 0:
        (here, d) = agenda[0]
        agenda = agenda[1:]
        if here == end:
            return d
        else:
            visited[here] = True
            agenda.extend([(neighbor, d+1) for neighbor in neighbors[here]
                           if neighbor not in visited])
    return None

class System(object):
    def __init__(self, sysname, sysid, jumps, sec, buying):
        self.sysname = sysname
        self.sysid = sysid
        self.jumps = jumps
        self.sec = sec
        self.vol = 0
        self.buying = buying
        self.stations = []

    def add_station(self, station):
        self.stations.append(station)

    def recalc(self):
        self.vol = 0
        for sta in self.stations:
            self.vol += sta.vol

    def showinfo(self):
        if IS_IGB:
            return ('<a href="showinfo:5//%s">%s</a>' %
                    (self.sysid, escape(self.sysname)))
        else:
            return ('<span class="showinfo">%s</span>' %
                    escape(self.sysname))

class Station(object):
    def __init__(self, staname, staid, statypeid):
        self.staname = staname
        self.staid = staid
        self.statypeid = statypeid
        self.vol = 0
        self.buying = False
        self.piles = []

    def add_pile(self, pile):
        self.piles.append(pile)
        self.vol += pile.vol
        if pile.buying:
            self.buying = True

    def showinfo(self):
        if IS_IGB:
            return ('<a href="showinfo:%s//%s">%s</a>' %
                    (self.statypeid, self.staid, escape(self.staname)))
        else:
            return ('<span class="showinfo">%s</span>' %
                    escape(self.staname))

class Pile(object):
    def __init__(self, typename, typeid, qty, vol, buying):
        self.typename = typename
        self.typeid = typeid
        self.qty = qty
        self.vol = vol
        self.buying = buying

    def showinfo(self):
        if IS_IGB:
            return ('<a href="showinfo:%s">%s</a>' %
                    (self.typeid, escape(self.typename)))
        else:
            return ('<span class="showinfo">%s</span>' %
                    escape(self.typename))

html_page_header = """
<?xml version="1.0"e encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
                      "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>GRD Deliveries</title>

<style type="text/css">
%(style)s
</style>

</head>

<body>
<h1>GRD Deliveries</h1>
<form action="%(script)s" method="GET">
<table>
  <tr>
    <td>Current&nbsp;System</td>
    <td><input type="text" name="system" size="13" value="%(system)s" /></td>
  </tr>
  <tr>
    <td>Type</td>
    <td><input type="text" name="type" size="13" value="%(type)s" /></td>
  <tr>
    <td>Volume</td>
    <td>Between&nbsp;<input type="text" name="minvol" size="4" value="%(minvol)s" />&nbsp;and&nbsp;<input type="text" name="maxvol" size="4" value="%(maxvol)s"/></td>
  </tr>
  <tr>
    <td>High-Sec&nbsp;Only</td>
    <td><input type="checkbox" name="safe" %(safe)s /></td>
  </tr>
  <tr>
    <td>Max&nbsp;Jumps</td>
    <td><input type="text" name="maxjumps" size="4" value="%(maxjumps)s" /></td>
  </tr>
</table>
<input type="submit" value="Update" />
</form>

<p>%(stats)s</p>

<table>
<tr>
  <th><a href="%(expandall)s">%(symbol)s</a></th>
  <th><a href="%(sortlocation)s">Location</a></th>
  <th><a href="%(sortvolume)s">Volume&nbsp;(m3)</a></th>
  <th><a href="%(sortjumps)s">Jumps</a></th>
  <th>Buying?</th>
</tr>
"""

html_system_row = """
<tr class="system">
  <td><a id="%(name)s" name="%(name)s" href="%(expand)s">%(symbol)s</a></td>
  <td>%(showinfo)s</td>
  <td class="right">%(volume)s</td>
  <td class="right">%(jumps)s</td>
  <td>%(buying)s</td>
</tr>
"""

html_station_row = """
<tr class="station">
  <td><a href="%(expand)s">%(symbol)s</a></td>
  <td>-&nbsp;%(showinfo)s</td>
  <td class="right">%(volume)s</td>
  <td></td>
  <td>%(buying)s</td>
</tr>
"""

html_pile_row = """
<tr class="pile">
  <td></td>
  <td>--&nbsp;%(showinfo)s&nbsp;x&nbsp;%(qty)s</td>
  <td class="right">%(volume)s</td>
  <td></td>
  <td>%(buying)s</td>
</tr>
"""

html_page_footer = """
</table>
</body> </html>
"""

css_igb = """
.highsec {
  color: #00FF00;
}

.lowsec {
  //color: #FFAF00;
  color: #FF0000;
}

.nullsec {
  color: #FF0000;
}

.yes {
  color: #00FF00;
}

.no {
  color: #FF0000;
}

td.right {
  text-align: right;
}

tr.system {
  background-color: #707F8F;
}

tr.station {
  background-color: #606F7F;
}

tr.pile {
  background-color: #505F6F;
}
"""

css_external = """
body {
  background: #202020;
  color: #DFDFDF;
  font-family: sans-serif;
}

a {
  color: #EFAF00;
  font-weight: bold;
}

a:visited {
  color: #EFAF00;
  font-weight: bold;
}

.showinfo {
  color: #EFAF00;
  font-weight: bold;
}

.yes {
  color: #00FF00;
  font-weight: bold;
}

.no {
  color: #FF0000;
  font-weight: bold;
}

.highsec {
  color: #00FF00;
  font-weight: bold;
}

.lowsec {
  //color: #FFAF00;
  color: #FF0000;
  font-weight: bold;
}

.nullsec {
  color: #FF0000;
  font-weight: bold;
}

td.right {
  text-align: right;
}

tr.system {
  background-color: #707F8F;
}

tr.station {
  background-color: #606F7F;
}

tr.pile {
  background-color: #505F6F;
}
"""


main()
