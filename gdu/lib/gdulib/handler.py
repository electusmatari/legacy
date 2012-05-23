import logging
import threading
import time

from gdulib.cacheutils import cache_load, make_methodcall

class Handler(threading.Thread):
    def __init__(self, control, fileq, dataq):
        super(Handler, self).__init__()
        self.daemon = True
        self.control = control
        self.fileq = fileq
        self.dataq = dataq
        self.uploaded = set()

    def run(self):
        while True:
            try:
                self.run2()
            except:
                self.control.exception("Exception during Handler run")
                time.sleep(10)

    def run2(self):
        # FIXME! We should clean up self.uploaded from time to time
        while True:
            filename = self.fileq.get()
            try:
                obj = cache_load(filename)
            except IOError:
                # We regularly get a "permission denied" when the file
                # is still locked, ignore this. We get a new notification
                # when the file is done
                continue
            except:
                self.control.exception("Can't load file %s" % filename)
                continue
            if len(obj) != 2:
                logging.info("Cache file isn't a method call: %s" % filename)
                continue
            methodcall = make_methodcall(obj[0])
            data = cache_dump(self.control, obj)
            if self.control.show_all_rpc_calls:
                logging.info("EVE RPC call: %s" % methodcall)
            if data is not None:
                key = filename, data['timestamp']
                if key not in self.uploaded:
                    self.uploaded.add(key)
                    self.dataq.put(data)

def cache_dump(control, obj):
    method = make_methodcall(obj[0], False)
    if not control.handle_method(method):
        return None
    timestamp = obj[1]['version'][0]
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
            if regionid != order.regionID:
                logging.warning("Order ID %s regionID (%s) differs from RPC "
                                "call regionID (%s)" % (order.orderID,
                                                        order.regionID,
                                                        regionid))
            if typeid != order.typeID:
                logging.warning("Order ID %s typeID (%s) differs from RPC "
                                "call typeID (%s)" % (order.orderID,
                                                      order.typeID,
                                                      typeid))
            if not hasattr(order, 'issueDate'):
                logging.info("Order ID %s (typeID %s) is rather old, "
                             "consider cleaning up your cache"
                             % (order.orderID,
                                order.typeID))
                break
            result.append(dict((name, getattr(order, name))
                               for name in [
                        'price', 'volRemaining', 'range', 'orderID',
                        'volEntered', 'minVolume', 'bid', 'issueDate',
                        'duration', 'stationID', 'solarSystemID', 'jumps'
                        # 'typeID', 'regionID'
                        ]))
        return {'method': self.method,
                'regionid': regionid,
                'typeid': typeid,
                'orders': result}

class FacWarDataHandler(object):
    method = 'map.GetFacWarData'
    display = "Victory points"
    description = """\
Upload current victory points when the occupation map is viewed\
"""

    def handle(self, obj):
        result = []
        for (sysid, (threshold, current, factionid)) in obj[1]['lret'].items():
            result.append({'factionid': factionid,
                           'systemid': sysid,
                           'threshold': threshold,
                           'current': current})
        return {'method': self.method,
                'map': result}

class LookupCharacterHandler(object):
    method = 'lookupSvc.LookupCharacters'
    display = "Pilot IDs"
    description = """\
Upload character IDs you search for in people & places (for evewho.com)\
"""

    def handle(self, obj):
        result = []
        for row in obj[1]['lret']:
            result.append(row.characterID)
        return {'method': self.method,
                'ids': result}


FILE_HANDLER = dict((h.method, h)
                    for h in [
        CorpFactionHandler(),
        FacWarDataHandler(),
        MarketHistoryHandler(),
        MarketOrderHandler(),
        LookupCharacterHandler(),
        ])

