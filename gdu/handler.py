import logging
import threading
import time

from cacheutils import cache_load, make_methodcall, wintime_to_datetime

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
            logging.info("Call: %s" % methodcall)
            data = cache_dump(self.control, obj)
            if data is not None:
                self.dataq.put(data)
                
def cache_dump(control, obj):
    method = make_methodcall(obj[0], False)
    timestamp = wintime_to_datetime(obj[1]['version'][0]
                                    ).strftime("%Y-%m-%d %H:%M:%S")
    handler = FILE_HANDLER.get(method)
    if handler is not None:
        return handler.handle(obj, timestamp)

class CorpFactionHandler(object):
    method = 'facWarMgr.GetCorporationWarFactionID'
    display = "Militia corporations"
    description = """\
Upload information about which militia a corporation you look at belongs to\
"""

    def handle(self, obj, timestamp):
        corpid = obj[0][2]
        factionid = obj[1]['lret']
        return {'method': self.method,
                'timestamp': timestamp,
                'corpid': corpid,
                'factionid': factionid}

class PlaceholderHandler(object):
    method = 'xyz'
    display = "Fnord"
    description = """\
Foo\
"""

                 
FILE_HANDLER = dict((h.method, h)
                    for h in [
        CorpFactionHandler(),
        PlaceholderHandler()
        ])
    
    
