import datetime
import threading

from django.db import connection

class Control(object):
    def __init__(self, conf):
        self.conf = conf
        self.stats = Stats()

class Stats(object):
    def __init__(self):
        # Number of feeds fetched
        self.numfeeds = CountInHours(24)
        # Number of feeds with errors
        self.numfeederrors = CountInHours(24)
        # Number of feeds disabled due to errors
        self.numfeeddisabled = CountInHours(24)
        # Number of kills fetched
        self.numkills = CountInHours(24)
        # Number of kills added to the DB
        self.numnewkills = CountInHours(24)
        # Number of kills deleted
        self.numkillsdeleted = CountInHours(24)

    def message(self):
        msg = ("In the last 24 hours, added %(numnewkills)s kills and "
               "deleted %(numkillsdeleted)s kills. Fetched a total of "
               "%(numkills)s kills from %(numfeeds)s feeds, of which "
               "%(numfeederrors)s had errors and %(numfeeddisabled)s were "
               "disabled."
               % {'numfeeds': int(self.numfeeds),
                  'numfeederrors': int(self.numfeederrors),
                  'numfeeddisabled': int(self.numfeeddisabled),
                  'numkills': int(self.numkills),
                  'numnewkills': int(self.numnewkills),
                  'numkillsdeleted': int(self.numkillsdeleted)
                  })
        c = connection.cursor()
        c.execute("SELECT COUNT(*) FROM intel_pilot "
                  "WHERE lastapi > NOW() - INTERVAL '24 hours'")
        (napicheck1,) = c.fetchone()
        c.execute("SELECT COUNT(*) FROM intel_corporation "
                  "WHERE lastapi > NOW() - INTERVAL '24 hours'")
        (napicheck2,) = c.fetchone()
        c.execute("SELECT COUNT(*) FROM intel_alliance "
                  "WHERE lastapi > NOW() - INTERVAL '24 hours'")
        (napicheck3,) = c.fetchone()
        napicheck = napicheck1 + napicheck2 + napicheck3
        if napicheck > 0:
            msg += " %s entities had their API details checked." % napicheck
        c.execute("SELECT COUNT(*) FROM intel_pilot WHERE NOT evewho")
        (nevewho,) = c.fetchone()
        if nevewho > 0:
            msg += " %s pilots need to be added to EVE Who." % nevewho
        c.execute("SELECT COUNT(*) FROM intel_kill WHERE NOT involved_added")
        (ninvolvedmissing,) = c.fetchone()
        if ninvolvedmissing > 0:
            msg += (" %s kills still need their involved parties added." %
                    ninvolvedmissing)
        return msg

class CountInHours(object):
    def __init__(self, hours):
        self.lock = threading.Lock()
        self.hours = datetime.timedelta(hours=hours)
        self.values = {}

    def _clean(self):
        now = datetime.datetime.now().replace(minute=0, second=0,
                                              microsecond=0)
        for ts in self.values.keys():
            if ts < now - self.hours:
                del self.values[ts]

    def __int__(self):
        with self.lock:
            self._clean()
            return sum(self.values.values())

    def sum(self):
        return int(self)

    def __iadd__(self, value):
        with self.lock:
            now = datetime.datetime.now().replace(minute=0, second=0,
                                                  microsecond=0)
            self.values.setdefault(now, 0)
            self.values[now] += value
            self._clean()
            return self
