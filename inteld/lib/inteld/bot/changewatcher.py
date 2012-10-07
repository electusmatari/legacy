import datetime
import logging
import threading
import time

from emtools.intel.models import Change

from django.db import connection

class ChangeWatcher(threading.Thread):
    def __init__(self, bot):
        super(ChangeWatcher, self).__init__()
        self.daemon = True
        self.bot = bot

    def run(self):
        while True:
            try:
                self.run2()
            except:
                logging.exception("Exception during changewatcher run")
                time.sleep(600)

    def run2(self):
        c = connection.cursor()
        c.execute("SELECT MAX(timestamp) FROM intel_change")
        (last,) = c.fetchone()
        if last is None:
            last = datetime.datetime.utcnow()
        while True:
            for change in Change.objects.filter(timestamp__gt=last
                                                ).order_by("timestamp"):
                if self.is_interesting(change):
                    self.bot.broadcast("[Intel] " + change.verbose())
            time.sleep(30)

    def is_interesting(self, change):
        if (change.oldfaction is not None and
            change.oldfaction.name == 'Amarr Empire'):
            return True
        if (change.newfaction is not None and
            change.newfaction.name == 'Amarr Empire'):
            return True
