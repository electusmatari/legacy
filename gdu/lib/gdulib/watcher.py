import logging
import os
import threading
import time

from gdulib.cacheutils import find_cache_directories

class Watcher(threading.Thread):
    def __init__(self, control, fileq):
        super(Watcher, self).__init__()
        self.daemon = True
        self.control = control
        self.fileq = fileq

    def run(self):
        while True:
            try:
                self.run2()
            except:
                logging.traceback("Exception during Watcher run")
                time.sleep(10)

    def run2(self):
        dir_list = find_cache_directories()
        if len(dir_list) == 0:
            logging.error("No cache directories found. Do you even have EVE "
                          "installed?")
        else:
            logging.info("Found cache directories in the following locations. "
                         "If you upgrade your EVE client, make sure to "
                         "restart the uploader.")
            for dirname in dir_list:
                logging.info("- %s" % dirname)
        w = DirectoryListWatcher(dir_list)
        for filename in w.new_files():
            self.fileq.put(filename)

class DirectoryListWatcher(object):
    def __init__(self, dirlist=[]):
        self.watcher = {}
        for dirname in dirlist:
            self.add_directory(dirname)

    def add_directory(self, dirname):
        self.watcher[dirname] = DirectoryWatcher(dirname)

    def new_files(self):
        while True:
            for dw in self.watcher.values():
                for filename in dw.get_new_files():
                    yield filename
            time.sleep(5)

class DirectoryWatcher(object):
    def __init__(self, dirname):
        self.dirname = dirname
        self.mtimes = {}
        list(self.get_new_files())

    def get_new_files(self):
        for filename in os.listdir(self.dirname):
            fullname = os.path.join(self.dirname, filename)
            stat = os.stat(fullname)
            if (fullname not in self.mtimes or
                stat.st_mtime > self.mtimes[fullname]):
                self.mtimes[fullname] = stat.st_mtime
                yield fullname
