import datetime
import logging
import os
import Queue
import shutil
import urllib
import webbrowser

import wx

from gdulib import rpc, version
from gdulib.cacheutils import find_cache_directories, find_cache_machodirs

from gdulib.status import Status
from gdulib.watcher import Watcher
from gdulib.handler import Handler
from gdulib.uploader import Uploader

class AppControl(object):
    def __init__(self):
        self.frame = None
        self.last_exception = None

    @property
    def auth_token(self):
        return self.frame.notebook.config.auth_token.GetValue()

    @property
    def auth_token_ok(self):
        return self.frame.notebook.config.auth_token_ok

    @property
    def show_all_rpc_calls(self):
        return self.frame.notebook.config.show_all_rpc_calls.GetValue()

    def status(self, text):
        self.frame.statusbar.SetStatusText(text)

    def handle_method(self, methodname):
        for cb in self.frame.notebook.config.checkboxes:
            if cb.option == methodname:
                return cb.GetValue()
        return True

    def exception(self, text):
        now = datetime.datetime.now()
        if (self.last_exception is None or
            (now - self.last_exception) > datetime.timedelta(minutes=5)):
            # Only once every 5 minutes
            rpc.submit_exception(self.auth_token, text)
            self.last_exception = now
        logging.exception(text)

    def configuration_problem(self, message, title="Configuration Problem",
                              style=wx.OK | wx.ICON_ERROR):
        if self.frame.IsIconized():
            self.frame.Iconize(False)
        if not self.frame.IsShown():
            self.frame.Show(True)
            self.frame.Raise()
        self.frame.notebook.ChangeSelection(0)
        return wx.MessageBox(message, title, style)

    def initialize(self, frame):
        self.frame = frame
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

    def check_version(self):
        current = float(urllib.urlopen("http://gradient.electusmatari.com/uploader/files/version.txt").read())
        if (current - version.VERSION) > 0.005:
            response = self.configuration_problem(
                "A new version of the Gradient Data Uploader is available.\n"
                "Your version: %.1f\n"
                "Available: %.1f\n"
                "Do you wish to download it?" % (version.VERSION, current),
                style=(wx.ICON_INFORMATION |
                       wx.YES_NO))
            if response == wx.YES:
                webbrowser.open("http://gradient.electusmatari.com/uploader/",
                                new=2)
            
    def check_token(self):
        if self.auth_token_ok:
            return True
        if self.auth_token == "":
            message = ("You have not configured an authentication token yet. "
                       "You will not be able to upload data until you have "
                       "done so.")
        else:
            message = ("The authentication token you have specified is "
                       "invaid. Please configure a correct token.")
        self.configuration_problem(message)
        return False

    def upload_existing(self):
        for dirname in find_cache_directories():
            for basedir, subdirs, filenames in os.walk(dirname):
                for filename in filenames:
                    self.fileq.put(os.path.join(basedir, filename))

    def clean_cache(self):
        for dirname in find_cache_machodirs():
            shutil.rmtree(dirname)
