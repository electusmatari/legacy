# Create your views here.

import datetime

from django.http import HttpResponse

import sys
sys.path.append("/home/forcer/Projects/evecode/web/gradient.electusmatari.com/data/python/")
from gradient.uploader.models import MarketHistory, MarketHistoryLastUpload
from gradient.uploader.models import MarketOrder, MarketOrderLastUpload
from gradient.uploader.models import FacWarSystem

from utils import APIResult, api_error

def markethistory(request):
    response = HttpResponse(content_type="text/xml")

    regionid = request.REQUEST.get('regionID', None)
    typeid = request.REQUEST.get('typeID', None)
    enddate = request.REQUEST.get('startdate', None)
    limit = request.REQUEST.get('limit', 7)
    if regionid is None:
        api_error(response, 150, "regionID must be specified")
        return response
    if typeid is None:
        api_error(response, 151, "typeID must be specified")
        return response
    if enddate is None:
        enddate = datetime.datetime.utcnow()
    else:
        try:
            enddate = datetime.datetime.strptime(enddate, "%Y-%m-%d %H:%M:%S")
        except:
            api_error(response, 152, "enddate must be specified and a valid date")
            return response
    if limit is None:
        limit = 7
    else:
        try:
            limit = min(int(limit), 30)
        except:
            api_error(response, 153, "limit must be an integer")
            return response
    try:
        lu = MarketHistoryLastUpload.objects.get(regionid=regionid,
                                               typeid=typeid
                                               ).cachetimestamp
    except MarketHistoryLastUpload.DoesNotExist:
        r = APIResult()
        r.writexml(response)
        return response
    r = APIResult(currentTime=lu, cached_hours=3)
    r.add_rowset('history', ['regionID', 'typeID', 'historyDate',
                             'lowPrice', 'highPrice', 'avgPrice',
                             'volume', 'orders'])
    for row in MarketHistory.objects.filter(regionid=regionid,
                                            typeid=typeid,
                                            historydate__lte=enddate
                                            ).order_by("-historydate")[0:limit]:
        r.add_row([('regionID', row.regionid),
                   ('typeID', row.typeid),
                   ('historyDate', row.historydate.strftime("%Y-%m-%d %H:%M:%S")),
                   ('lowPrice', row.lowprice),
                   ('highPrice', row.highprice),
                   ('avgPrice', row.avgprice),
                   ('volume', row.volume),
                   ('orders', row.orders)])
    r.writexml(response)
    return response

def marketorders(request):
    response = HttpResponse(content_type="text/xml")

    regionid = request.REQUEST.get('regionID', None)
    typeid = request.REQUEST.get('typeID', None)
    if regionid is None:
        api_error(response, 150, "regionID must be specified")
        return response
    if typeid is None:
        api_error(response, 151, "typeID must be specified")
        return response
    try:
        lu = MarketOrderLastUpload.objects.get(regionid=regionid,
                                               typeid=typeid
                                               ).cachetimestamp
    except MarketOrderLastUpload.DoesNotExist:
        r = APIResult()
        r.writexml(response)
        return response
    r = APIResult(currentTime=lu, cached_hours=3)
    r.add_rowset('history', ['orderID', 'stationID', 'solarSystemID',
                             'regionID', 'volEntered', 'volRemaining',
                             'minVolume', 'typeID', 'range', 'duration',
                             'price', 'bid', 'issueDate'], key='orderID')
    for row in MarketOrder.objects.filter(regionid=regionid,
                                          typeid=typeid):
        r.add_row([('orderID', row.orderid),
                   ('stationID', row.stationid),
                   ('solarSystemID', row.solarsystemid),
                   ('regionID', row.regionid),
                   ('volEntered', row.volentered),
                   ('volRemaining', row.volremaining),
                   ('minVolume', row.minvolume),
                   ('typeID', row.typeid),
                   ('range', row.range),
                   ('duration', row.duration),
                   ('price', row.price),
                   ('bid', row.bid),
                   ('issueDate', row.issuedate),
                   ])
    r.writexml(response)
    return response

def fwsystems(request):
    from django.core.exceptions import PermissionDenied
    raise PermissionDenied()
    response = HttpResponse(content_type="text/xml")
    lu = FacWarSystem.objects.all()[0].cachetimestamp
    r = APIResult(currentTime=lu, cached_hours=1)
    r.add_rowset('solarSystems', ['solarSystemID', 'solarSystemName',
                                  'occupyingFactionID', 'owningFactionID',
                                  'occupyingFactionName', 'owningFactionName',
                                  'contested', 'victoryPoints', 'threshold'],
                 'solarSystemID')
    for fws in FacWarSystem.objects.all().order_by('solarsystemid'):
        r.add_row([('solarSystemID', fws.solarsystemid),
                   ('solarSystemName', fws.solarsystemname),
                   ('occupyingFactionID', fws.occupyingfactionid),
                   ('owningFactionID', fws.owningfactionid),
                   ('occupyingFactionName', fws.occupyingfactionname),
                   ('owningFactionName', fws.owningfactionname),
                   ('contested', fws.victorypoints > 0),
                   ('victoryPoints', fws.victorypoints),
                   ('threshold', fws.threshold)
                   ])
    r.writexml(response)
    return response
