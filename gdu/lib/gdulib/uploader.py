import json
import logging
import threading
import time

class Uploader(threading.Thread):
    def __init__(self, control, dataq):
        super(Uploader, self).__init__()
        self.daemon = True
        self.control = control
        self.dataq = dataq

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
            logging.info("Upload: %s" % json.dumps(data))
