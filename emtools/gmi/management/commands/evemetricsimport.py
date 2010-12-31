from django.core.management.base import BaseCommand, CommandError

import csv
import bz2
import datetime
import urllib
import logging

from emtools.ccpeve.models import MarketHistory

HISTORIC_URL = "http://export.eve-metrics.com/historic/%s.csv.bz2"

REGIONIDS = ['10000002', '10000011', '10000028', '10000030',
             '10000042']

log = logging.getLogger('gmi')

class Command(BaseCommand):
    args = ""
    help = "Import market history from EVE Metrics"

    def handle(self, *args, **options):
        evemetricsimport()

def evemetricsimport():
    today = datetime.date.today()
    newentries = 0
    start = datetime.datetime.now()
    for regionid in REGIONIDS:
        known = set()
        currtypeid = None
        cdata = urllib.urlopen(HISTORIC_URL % regionid).read()
        reader = csv.reader(bz2.decompress(cdata).split("\n"))
        reader.next() # Skip header
        for row in reader:
            if len(row) != 7:
                continue
            (typeid, orders, movement, max, avg, min, date) = row
            rowdate = datetime.datetime.strptime(date, "%Y-%m-%d").date()
            if typeid != currtypeid:
                currtypeid = typeid
                known = set()
                for mh in MarketHistory.objects.filter(regionid=regionid,
                                                       typeid=typeid):
                    known.add(mh.historydate.strftime("%Y-%m-%d"))
            if date in known:
                continue
            newentries += 1
            MarketHistory.objects.create(
                regionid=regionid,
                typeid=typeid,
                historydate=date,
                lowprice=min,
                highprice=max,
                avgprice=avg,
                volume=movement,
                orders=orders)
    end = datetime.datetime.now()
    log.info("Market history imported %s new entries from eve-metrics in %s" %
             (newentries, end - start))
