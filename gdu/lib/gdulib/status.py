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
        self.numdirs = 0
        self.numfiles = 0
        self.numbytes = 0

    def run(self):
        while True:
            try:
                self.run2()
            except:
                self.control.exception("Exception during Status run")
                time.sleep(10)

    def run2(self):
        while True:
            self.control.status(
                "Watching %s %s, uploaded %s in %s %s, "
                "parse queue %s, upload queue %s" %
                (self.numdirs,
                 "directory" if self.numdirs == 1 else "directories",
                 sizestring(self.numbytes),
                 self.numfiles,
                 "file" if self.numfiles == 1 else "files",
                 self.fileq.qsize(),
                 self.dataq.qsize())
                )
            time.sleep(0.5)

def sizestring(numbytes):
    if numbytes < 1024:
        return "%s bytes" % numbytes
    elif numbytes < 1024 * 1024:
        return "%.1f kB" % (numbytes / 1024.0)
    else:
        return "%.1f MB" % (numbytes / 1024.0 / 1024.0)
