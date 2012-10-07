import logging
import re

from urllib import urlencode
from urllib2 import urlopen

log = logging.getLogger('bc')

KILLID_RX = re.compile(r'killmail.php\?id=(?P<killid>[0-9]+)')

def getrepublic(lastkillid):
    killids = []
    newlastkillid = lastkillid
    for region in ['Heimatar', 'Metropolis', 'Molden Heath']:
        page = 0
        for page in range(1, 21):
            url = 'http://eve.battleclinic.com/killboard/recent_activity.php'
            data = urlencode([('searchTerms', region),
                              ('page', str(page))])
            f = urlopen(url, data)
            for killid in KILLID_RX.findall(f.read()):
                killid = int(killid)
                newlastkillid = max(killid, newlastkillid)
                if killid > lastkillid:
                    killids.append(killid)
    killinfos = []
    for killid in killids:
        ki = get_killinfo(killid)
        if ki is None:
            log.error("Error retrieving battleclinic kill mail %s" %
                      killid)
        killinfos.append(ki)
    return newlastkillid, killinfos

KILLINFO_RX = re.compile(r'<textarea name="killmail" cols="50" rows="30" readonly="readonly">((?:\n|.)*)</textarea>')

def get_killinfo(killid):
    url = 'http://eve.battleclinic.com/killboard/killmail.php'
    data = urlencode([('id', killid),
                      ('format', 'original')])
    f = urlopen(url, data)
    data = f.read()
    m = KILLINFO_RX.match(data)
    if m is None:
        return data
    else:
        return m.group(1)
