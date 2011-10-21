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
                logging.exception("Exception during watching of %s" % dirname)
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
        while True:
            results = win32file.ReadDirectoryChangesW (
                handle,
                1024,
                True,
                win32con.FILE_NOTIFY_CHANGE_FILE_NAME |
                win32con.FILE_NOTIFY_CHANGE_DIR_NAME |
                win32con.FILE_NOTIFY_CHANGE_ATTRIBUTES |
                win32con.FILE_NOTIFY_CHANGE_SIZE |
                win32con.FILE_NOTIFY_CHANGE_LAST_WRITE |
                win32con.FILE_NOTIFY_CHANGE_SECURITY,
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

# class DirectoryListWatcher(object):
#     def __init__(self, dirlist=[]):
#         self.watcher = {}
#         for dirname in dirlist:
#             self.add_directory(dirname)
# 
#     def add_directory(self, dirname):
#         self.watcher[dirname] = DirectoryWatcher(dirname)
# 
#     def new_files(self):
#         while True:
#             for dw in self.watcher.values():
#                 for filename in dw.get_new_files():
#                     yield filename
#             time.sleep(5)
# 
# class DirectoryWatcher(object):
#     def __init__(self, dirname):
#         self.dirname = dirname
#         self.mtimes = {}
#         list(self.get_new_files())
# 
#     def get_new_files(self):
#         for filename in os.listdir(self.dirname):
#             fullname = os.path.join(self.dirname, filename)
#             stat = os.stat(fullname)
#             if (fullname not in self.mtimes or
#                 stat.st_mtime > self.mtimes[fullname]):
#                 self.mtimes[fullname] = stat.st_mtime
#                 yield fullname
