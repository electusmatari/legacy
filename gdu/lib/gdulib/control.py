import Queue

from gdulib import api

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

    def exit(self):
        self.frame.Close(True)

    def status(self, text):
        self.frame.statusbar.SetStatusText(text)

    def is_configured_correctly(self):
        auth_token = self.auth_token
        if not api.check_auth_token(auth_token):
            return False
        return True

    def initialize(self):
        self.fileq = Queue.Queue()
        self.dataq = Queue.Queue()
        s = Status(self, self.fileq, self.dataq)
        s.start()
        w = Watcher(self, self.fileq)
        w.start()
        h = Handler(self, self.fileq, self.dataq)
        h.start()
        u = Uploader(self, self.dataq)
        u.start()
    
