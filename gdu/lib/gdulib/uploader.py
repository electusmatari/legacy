import json
import logging
import threading
import time

from gdulib import rpc

class Uploader(threading.Thread):
    def __init__(self, control, dataq, stats):
        super(Uploader, self).__init__()
        self.daemon = True
        self.control = control
        self.dataq = dataq
        self.stats = stats

    def run(self):
        while True:
            try:
                self.run2()
            except:
                self.control.exception("Exception during Uploader run")
                time.sleep(10)

    def run2(self):
        while not self.control.auth_token_ok:
            time.sleep(60)
        while True:
            data = self.dataq.get()
            self.stats.numfiles += 1
            json_data = json.dumps(data)
            self.stats.numbytes += len(json_data)
            try:
                response = rpc.submit_cache_data(self.control.auth_token,
                                                 data)
            except rpc.RPCError as e:
                logging.error("RPC error %s" % str(e))
            except Exception as e:
                logging.error("Error %s during upload: %s" %
                              (e.__class__.__name__,
                               str(e)))
