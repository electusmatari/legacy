import datetime
import time
import logging
import threading

from django.db import connection
from django.db.models import Q

from emtools.ccpeve import eveapi
from emtools.ccpeve.models import apiroot
from emtools.intel.models import Pilot, Corporation, Alliance, NotOnAPIError

from inteld.utils import get_standings

class APICheck(threading.Thread):
    def __init__(self, ctrl):
        super(APICheck, self).__init__()
        self.daemon = True
        self.status = "Starting up"
        self.ctrl = ctrl

    def run(self):
        while True:
            try:
                self.run2()
            except:
                connection._rollback()
                logging.exception("Exception during APICheck run")
                time.sleep(60*10)

    def run2(self):
        lastdaily = 0
        while True:
            if time.time() > lastdaily + 60*60*12: # Once a day
                lastdaily = time.time()
                self.do_daily()
            self.status = "Checking entities with do_api_check=True"
            self.check(Alliance, do_api_check=True)
            self.check(Corporation, do_api_check=True)
            self.check(Pilot, do_api_check=True)
            self.status = "Checking entities with no api check"
            self.check(Alliance, lastapi=None)
            self.check(Corporation, lastapi=None)
            self.check(Pilot, lastapi=None)

            self.status = "Checking Factional Warfare corporations"
            old = datetime.datetime.now() - datetime.timedelta(days=1)
            self.check(Corporation, ~Q(faction__isnull=True),
                       lastapi__lt=old)

            self.status = "Checking tracked entities"
            self.check(Alliance, ~Q(trackedentity__isnull=True),
                       lastapi__lt=old)
            self.check(Corporation, ~Q(trackedentity__isnull=True),
                       lastapi__lt=old)
            self.check(Pilot, ~(Q(corporation=None) |
                                Q(corporation__trackedentity__isnull=True)),
                       lastapi__lt=old)
            self.check(Pilot, ~(Q(alliance=None) |
                                Q(alliance__trackedentity__isnull=True)),
                       lastapi__lt=old)
            self.check(Pilot, ~(Q(corporation=None) |
                                Q(corporation__alliance=None) |
                                Q(corporation__alliance__trackedentity__isnull=True)),
                       lastapi__lt=old)

            connection._commit()
            self.status = "Sleeping"
            time.sleep(60)

    def check(self, Model, *args, **kwargs):
        for obj in Model.objects.filter(*args, **kwargs):
            try:
                obj.apicheck()
            except eveapi.Error as e:
                if e.code in (105, 522, 523):
                    obj.lastapi = datetime.datetime.utcnow()
                    obj.active = False
                    obj.do_api_check = False
                    obj.save()
                else:
                    raise

    def do_daily(self):
        self.status = "Checking FacWarTopStats"
        self.facwartopstats()
        self.status = "Checking alliance standings"
        self.standings()

    def facwartopstats(self):
        api = apiroot()
        fwts = api.eve.FacWarTopStats()
        charids = set()
        corpids = set()
        for rowset in ('KillsYesterday', 'KillsLastWeek', 'KillsTotal',
                       'VictoryPointsYesterday', 'VictoryPointsLastWeek',
                       'VictoryPointsTotal'):
            for row in getattr(fwts.characters, rowset):
                charids.add(row.characterID)
            for row in getattr(fwts.corporations, rowset):
                corpids.add(row.corporationID)
            for charid in charids:
                obj, created = Pilot.objects.get_or_create_from_api(
                    characterid=charid)
                if not created:
                    obj.apicheck()
            for corpid in corpids:
                obj, created = Corporation.objects.get_or_create_from_api(
                    corporationid=corpid)
                if not created:
                    obj.apicheck()
                if obj.corporationid >= 98000000: # Not an NPC corp
                    obj.do_cache_check = True
                obj.save()

    def standings(self):
        c = connection.cursor()
        c.execute("UPDATE intel_corporation SET standing = NULL")
        c.execute("UPDATE intel_alliance SET standing = NULL")
        api = apiroot()
        alliances = set(row.allianceID
                        for row in api.eve.AllianceList().alliances)
        for itemid, standing in get_standings().items():
            if itemid in alliances:
                obj, created = Alliance.objects.get_or_create_from_api(
                    allianceid=itemid)
            else:
                try:
                    obj, created = Corporation.objects.get_or_create_from_api(
                        corporationid=itemid)
                except NotOnAPIError:
                    continue
            if not created:
                obj.apicheck()
            obj.standing = standing
            obj.save()
