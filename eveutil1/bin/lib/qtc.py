# Library interface to the QTC Matari Mineral Index (MMI), Matari
# Datacore Index (MDI), and Matari Salvage Index (MSI).

import re
import urllib
from xml.etree.ElementTree import fromstring as parse_xml

url = "http://www.starvingpoet.net/feeds/mmi.xml"

def qtc7():
    (date, index) = qtc()
    return dict((name, value)
                for (name, (value, volume))
                in index[7].items())

def qtc():
    data = urllib.urlopen(url).read()
    xml = parse_xml(data)
    date = xml.get("date")
    index = {}
    for group in xml.findall("index"):
        this = {}
        timeperiod = int(group.get("timeperiod"))
        for item in group.getchildren():
            name = fixname(item.tag)
            price = float(item.find("price").text)
            volume = float(item.find("volume").text)
            this[name] = (price, volume)
        index[timeperiod] = this
    return (date, index)

rx = re.compile("[A-Z-][^A-Z-]*")
def fixname(str):
    return " ".join(rx.findall(str))
