import logging
import Queue

from gdulib import rpc, version

from gdulib.status import Status
from gdulib.watcher import Watcher
from gdulib.handler import Handler
from gdulib.uploader import Uploader

class AppControl(object):
    def __init__(self, frame):
        self.frame = frame
        self.initialize()

    @property
    def auth_token(self):
        return self.frame.notebook.config.auth_token.GetValue()

    @property
    def show_all_rpc_calls(self):
        return self.frame.notebook.config.show_all_rpc_calls.GetValue()

    def status(self, text):
        self.frame.statusbar.SetStatusText(text)

    def handle_method(self, methodname):
        for cb in self.frame.checkboxes:
            if cb.option == methodname:
                return cb.GetValue()
        return True

    def is_configured_correctly(self):
        auth_token = self.auth_token
        if not rpc.check_auth_token(auth_token):
            return False
        return True

    def initialize(self):
        logging.info("%s %s starting." % (version.APPLONGNAME,
                                          version.VERSIONSTRING))
        logging.info("Freedom through strength. Strength through superior "
                     "datamining.")
        self.fileq = Queue.Queue()
        self.dataq = Queue.Queue()
        s = Status(self, self.fileq, self.dataq)
        s.start()
        w = Watcher(self, self.fileq, s)
        w.start()
        h = Handler(self, self.fileq, self.dataq)
        h.start()
        u = Uploader(self, self.dataq, s)
        u.start()
