import logging
import os
import threading
import time

import win32file
import win32con

from gdulib.cacheutils import find_cache_directories

class Watcher(threading.Thread):
    def __init__(self, control, fileq, stats):
        super(Watcher, self).__init__()
        self.daemon = True
        self.control = control
        self.fileq = fileq
        self.stats = stats

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
            self.control.configuration_problem(
                "Could not find an EVE installation. If you do indeed have "
                "an EVE client installed, please notify the author. "
                "Otherwise, please install an EVE client to use this "
                "software."
                )
            logging.error("No cache directories found. Do you even have EVE "
                          "installed?")
        else:
            for dirname in dir_list:
                logging.info("Watching %s" % dirname)
                t = threading.Thread(target=self.watch_single_dir,
                                     args=(dirname,))
                t.daemon = True
                t.start()
                self.stats.numdirs += 1
        # FIXME! Watch the main cache directories <.<
        while True:
            time.sleep(60)

    def watch_single_dir(self, dirname):
        while True:
            try:
                self.watch_single_dir2(dirname)
            except:
                self.control.exception("Exception during watching of %s" %
                                       dirname)
                time.sleep(10)

    def watch_single_dir2(self, dirname):
        handle = win32file.CreateFile (
            dirname,
            0x0001, # FILE_LIST_DIRECTORY
            win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE,
            None,
            win32con.OPEN_EXISTING,
            win32con.FILE_FLAG_BACKUP_SEMANTICS,
            None
            )
        i = 0
        while True:
            i += 1
            results = win32file.ReadDirectoryChangesW (
                handle,
                1024,
                True,
                win32con.FILE_NOTIFY_CHANGE_FILE_NAME |
                win32con.FILE_NOTIFY_CHANGE_DIR_NAME |
                win32con.FILE_NOTIFY_CHANGE_ATTRIBUTES |
                win32con.FILE_NOTIFY_CHANGE_SIZE |
                win32con.FILE_NOTIFY_CHANGE_LAST_WRITE |
                win32con.FILE_NOTIFY_CHANGE_SECURITY
                ,
                None,
                None
                )
            for action, filename in results:
                # 1: Created
                # 2: Deleted
                # 3: Updated
                # 4: Renamed from something
                # 5: Renamed to something
                if action == 3: # We get 1, 3 in short succession for
                                # a new file
                    self.fileq.put(os.path.join(dirname, filename))
