import json
import logging
import threading
import time

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
                logging.exception("Exception during Uploader run")
                time.sleep(10)

    def run2(self):
        while True:
            data = self.dataq.get()
            self.stats.numfiles += 1
            self.stats.numbytes += len(json.dumps(data))
            # FIXME! Use api.py and self.control.auth_token :o)
