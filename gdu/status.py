import logging
import threading
import time

class Status(threading.Thread):
    def __init__(self, control, fileq, dataq):
        super(Status, self).__init__()
        self.daemon = True
        self.control = control
        self.fileq = fileq
        self.dataq = dataq

    def run(self):
        while True:
            try:
                self.run2()
            except:
                logging.exception("Exception during Status run")
                time.sleep(10)

    def run2(self):
        while True:
            self.control.status(
                "fileq %s, dataq %s" %
                (self.fileq.qsize(),
                 self.dataq.qsize())
                )
            time.sleep(0.5)
