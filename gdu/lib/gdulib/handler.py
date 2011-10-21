import logging
import threading
import time

from gdulib.cacheutils import cache_load, make_methodcall, wintime_to_datetime

class Handler(threading.Thread):
    def __init__(self, control, fileq, dataq):
        super(Handler, self).__init__()
        self.daemon = True
        self.control = control
        self.fileq = fileq
        self.dataq = dataq

    def run(self):
        while True:
            try:
                self.run2()
            except:
                logging.exception("Exception during Handler run")
                time.sleep(10)

    def run2(self):
        while True:
            filename = self.fileq.get()
            try:
                obj = cache_load(filename)
            except:
                logging.exception("Can't load file %s" % filename)
                continue
            if len(obj) != 2:
                logging.info("Cache file isn't a method call: %s" % filename)
                continue
            methodcall = make_methodcall(obj[0])
            data = cache_dump(self.control, obj)
            if self.control.show_all_rpc_calls:
                logging.info("RPC call: %s" % methodcall)
            if data is not None:
                self.dataq.put(data)
                
def cache_dump(control, obj):
    method = make_methodcall(obj[0], False)
    if not control.handle_method(method):
        return None
    timestamp = wintime_to_datetime(obj[1]['version'][0]
                                    ).strftime("%Y-%m-%d %H:%M:%S")
    handler = FILE_HANDLER.get(method)
    if handler is not None:
        d = handler.handle(obj)
        d['timestamp'] = timestamp
        return d

class CorpFactionHandler(object):
    method = 'facWarMgr.GetCorporationWarFactionID'
    display = "Militia corporations"
    description = """\
Upload information about which militia a corporation you look at belongs to\
"""

    def handle(self, obj):
        corpid = obj[0][2]
        factionid = obj[1]['lret']
        return {'method': self.method,
                'corpid': corpid,
                'factionid': factionid}

class MarketHistoryHandler(object):
    method = 'marketProxy.GetOldPriceHistory'
    display = "Market history"
    description = """\
Upload the market history for items viewed in the market window\
"""

    def handle(self, obj):
        regionid = obj[0][2]
        typeid = obj[0][3]
        result = []
        for row in obj[1]['lret']:
            result.append({'historyDate': row.historyDate,
                           'lowPrice': row.lowPrice,
                           'highPrice': row.highPrice,
                           'avgPrice': row.avgPrice,
                           'volume': row.volume,
                           'orders': row.orders})
        return {'method': self.method,
                'regionid': regionid,
                'typeid': typeid,
                'history': result}

class MarketOrderHandler(object):
    method = 'marketProxy.GetOrders'
    display = "Market orders"
    description = """\
Upload current buy and sell orders when the market is viewed\
"""

    def handle(self, obj):
        regionid = obj[0][2]
        typeid = obj[0][3]
        sellorder, buyorder = obj[1]['lret']
        result = []
        for order in sellorder + buyorder:
            result.append(dict((name, getattr(order, name))
                               for name in [
                        'price', 'volRemaining', 'typeID', 'range', 'orderID',
                        'volEntered', 'minVolume', 'bid', 'issueDate',
                        'duration', 'stationID', 'regionID', 'solarSystemID',
                        'jumps'
                        ]))
        return {'method': self.method,
                'regionid': regionid,
                'typeid': typeid,
                'orders': result}

class VictoryPointsHandler(object):
    method = 'map.GetVictoryPoints'
    display = "Victory points"
    description = """\
Upload current victory points when the occupation map is viewed\
"""

    def handle(self, obj):
        result = []
        for factionid, details in obj[1]['lret'].items():
            for sysid, threshold, current in details['defending']:
                if current == 0:
                    continue
                result.append({'faction': factionid,
                               'system': sysid,
                               'threshold': threshold,
                               'current': current})
        return {'method': self.method,
                'map': result}


FILE_HANDLER = dict((h.method, h)
                    for h in [
        CorpFactionHandler(),
        VictoryPointsHandler(),
        MarketHistoryHandler(),
        MarketOrderHandler(),
        ])

