# EDK feed parser

import logging
import datetime
import re
import urllib
import xml.etree.ElementTree as ET

MIRROR_WEEKS = 12

log = logging.getLogger('edk')

def getfeed(feedurl, lastkillid=None, master=True):
    """
    Retrieve kills from the feed, starting at lastkillid, or at least
    the last 12 weeks. Returns a tuple of the new lastkillid and the
    list of kill mails.
    """
    baseurl = feedurl + "&combined=1"
    if master:
        baseurl += "&master=1"
    result = []
    if lastkillid is None:
        killid = 0
        now = datetime.datetime.utcnow()
        oneweek = datetime.timedelta(days=7)
        for count in range(MIRROR_WEEKS):
            date = now - count * oneweek
            year = date.year
            week = int(date.strftime("%W"))
            (newlastkillid, killmails) = getfeed_single("%s&year=%s&week=%s" %
                                                        (baseurl, year, week))
            killid = max(killid, newlastkillid)
            result.extend(killmails)
    else:
        killid = lastkillid
        for ignored in range(10): # Only 10 iterations max
            (newlastkillid, killmails) = getfeed_single("%s&lastkllid=%s" %
                                                        (baseurl, killid))
            killid = max(killid, newlastkillid)
            result.extend(killmails)
            if len(killmails) < 100:
                break
    if len(result) == 0 and master is True:
        return getfeed(feedurl, lastkillid, False)
    else:
        return killid, result

def getfeed_single(feedurl, urlopen=urllib.urlopen):
    lastkillid = 0
    killinfos = []
    try:
        xml = urlopen(feedurl).read()
    except Exception as e:
        log.error("Error %s while reading URL %s: %s" %
                  (e.__class__.__name__, feedurl, str(e)))
        raise
    try:
        tree = get_tree(xml)
    except BypassParsingException as result:
        return result.value
    except Exception as e:
        log.error("Error %s while parsing URL %s: %s" %
                  (e.__class__.__name__, feedurl, str(e)))
        return (0, [])
    if tree is None:
        log.error("Can't parse XML from URL %s" %
                  (feedurl,))
        return (0, [])
    for item in tree.findall("channel/item"):
        killid = int(item.find("title").text)
        killinfo = item.find("description").text
        lastkillid = max(killid, lastkillid)
        killinfos.append(killinfo.strip() + "\n")
    return lastkillid, killinfos

def get_tree(xml):
    """
    EDK XML generation is horribad.
    """
    # Try normal
    try:
        return ET.fromstring(xml)
    except Exception:
        pass
    # Try removing stuff before the beginning and after the end
    if '<?xml' in xml and '</rss>' in xml:
        xml = xml[xml.index("<?xml"):]
        xml = xml[:xml.index("</rss>")+6]
        try:
            return ET.fromstring(xml)
        except Exception:
            pass
    # The RSS title isn't escaped
    xml = xml.replace(">YARR & Co<", ">YARR &amp; Co<")
    try:
        return ET.fromstring(xml)
    except Exception:
        pass
    # 8-bit characters aren't properly escaped, either
    for c in range(127, 256):
        xml = xml.replace(chr(c), "&x%x;" % c)
    try:
        return ET.fromstring(xml)
    except Exception:
        pass
    # And there is a generation bug
    if "Database error: Duplicate entry" in xml:
        match = re.search(r'VALUES\(([0-9]*), ', xml)
        if match is not None:
            raise BypassParsingException((int(match.group(1)) + 1, []))
    # Give up
    log.error("Error parsing XML")
    return None
        
    
class BypassParsingException(Exception):
    def __init__(self, value):
        self.value = value
        super(BypassParsingException, self).__init__()
