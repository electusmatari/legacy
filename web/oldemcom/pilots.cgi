#!/usr/bin/python

import cgitb
cgitb.enable()

import urllib, re, cgi

def main():
    print "Content-Type: text/html"
    print
    print "<html><head><title>Pilot Links</title></head>"
    print "<body><h1>Pilot Links</h1>"
    form = cgi.FieldStorage()
    names = form.getfirst("names", None)
    if names:
        action_show(names)
    else:
        action_entry()
    print "</body>"

def action_entry():
    print """
<form action="pilots.cgi" method="post">
<p>Please enter pilot names, one per line:</p>
<textarea name="names">
</textarea><br>
<input type="submit">
</form>
"""

def action_show(names):
    namelist = [s.strip() for s in names.split("\n")]
    showlinks(get_character_ids(namelist))

def showlinks(people):
    print "<p>Links:</p>"
    if len(people) == 0:
        print "Some pilot names not found, or the DB server is down."
    else:
        for (name, charid) in people:
            print ('<a href="showinfo:1379//%s">%s</a><br>'
                   % (charid, name))
    print '<p><a href="pilots.cgi">Get more links</a></p>'

charid_rx = re.compile('name="([^"]*)" characterID="([^"]*)"')

def get_character_ids(names):
    commalist = ",".join(names)
    quoted = urllib.quote(commalist)
    url = urllib.urlopen("http://api.eve-online.com/eve/CharacterID.xml.aspx?names="
                         + quoted)
    data = url.read()
    return charid_rx.findall(data)

main()
