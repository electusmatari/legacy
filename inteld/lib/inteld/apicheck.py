from collections import deque
import datetime
import time
import logging
import threading

from django.db import connection
from django.db.models import Q

from emtools.ccpeve import eveapi
from emtools.ccpeve.models import apiroot
from emtools.intel.models import Pilot, Corporation, Alliance, Change

from inteld.utils import get_standings, get_ownerid

class APICheck(threading.Thread):
    def __init__(self, ctrl):
        super(APICheck, self).__init__()
        self.daemon = True
        self.ctrl = ctrl

    def run(self):
        while True:
            try:
                self.run2()
            except:
                logging.exception("Exception during APICheck run")

    def run2(self):
        per_run = 12 * 60 * 60
        while True:
            next_run = time.time() + per_run
            self.single_run()
            now = time.time()
            if now < next_run:
                time.sleep(next_run - now)

    def single_run(self):
        start = datetime.datetime.now()
        self.get_entityids()
        self.add_facwartopstats()
        self.update_alliances()
        self.update_standings()
        agenda = deque(self.collect_agenda())
        agendalen = len(agenda)
        per_check = (6.0 * 60 * 60) / agendalen
        logging.info("Checking %i entities (%.1fs per entity)" %
                     (agendalen, per_check))
        while len(agenda) > 0:
            next_check = time.time() + per_check
            self.check(agenda.popleft())
            now = time.time()
            if now < next_check:
                time.sleep(next_check - now)
        end = datetime.datetime.now()
        logging.info("Checked %s entities in %s" % (agendalen,
                                                    (end - start)))

    def get_entityids(self):
        for pilot in Pilot.objects.filter(characterid=None):
            itemid = get_ownerid(pilot.name)
            if itemid is None or itemid == 0:
                logging.info("Deleting pilot %r (no itemID found)" %
                             pilot.name)
                pilot.kill_set.clear()
                Change.objects.filter(Q(pilot=corp) |
                                      Q(oldpilot=corp) |
                                      Q(newpilot=corp)).delete()
                pilot.delete()
            else:
                try:
                    other = Pilot.objects.get(characterid=itemid)
                except Pilot.DoesNotExist:
                    pilot.characterid = itemid
                    pilot.save()
                else:
                    for kill in pilot.kill_set.all():
                        other.kill_set.add(kill)
                    pilot.kill_set.clear()
                    for change in Change.objects.filter(Q(pilot=pilot) |
                                                        Q(oldpilot=pilot) |
                                                        Q(newpilot=pilot)):
                        if change.pilot == pilot:
                            change.pilot = other
                        if change.oldpilot == pilot:
                            change.oldpilot = other
                        if change.newpilot == pilot:
                            change.newpilot = other
                        change.save()
                    pilot.delete()
        for corp in Corporation.objects.filter(corporationid=None):
            itemid = get_ownerid(corp.name)
            if itemid is None or itemid == 0:
                logging.info("Deleting corp %r (no itemID found)" % corp.name)
                corp.kill_set.clear()
                Change.objects.filter(Q(corporation=corp) |
                                      Q(oldcorp=corp) |
                                      Q(newcorp=corp)).delete()
                corp.delete()
            else:
                try:
                    other = Corporation.objects.get(corporationid=itemid)
                except Corporation.DoesNotExist:
                    corp.corporationid = itemid
                    corp.save()
                else:
                    for kill in corp.kill_set.all():
                        other.kill_set.add(kill)
                    corp.kill_set.clear()
                    for change in Change.objects.filter(Q(corporation=corp) |
                                                        Q(oldcorp=corp) |
                                                        Q(newcorp=corp)):
                        if change.corporation == corp:
                            change.corporation = other
                        if change.oldcorp == corp:
                            change.oldcorp = other
                        if change.newcorp == corp:
                            change.newcorp = other
                        change.save()
                    corp.delete()
        for ally in Alliance.objects.filter(allianceid=None):
            itemid = get_ownerid(ally.name)
            if itemid is None or itemid == 0:
                logging.info("Deleting alliance %r (no itemID found)" %
                             ally.name)
                ally.kill_set.clear()
                Change.objects.filter(Q(alliance=ally) |
                                      Q(oldalliance=ally) |
                                      Q(newalliance=ally)).delete()
                ally.delete()
            else:
                try:
                    other = Alliance.objects.get(allianceid=itemid)
                except Alliance.DoesNotExist:
                    ally.characterid = itemid
                    ally.save()
                else:
                    for kill in ally.kill_set.all():
                        other.kill_set.add(kill)
                    ally.kill_set.clear()
                    for change in Change.objects.filter(Q(alliance=ally) |
                                                        Q(oldalliance=ally) |
                                                        Q(newalliance=ally)):
                        if change.alliance == ally:
                            change.alliance = other
                        if change.oldalliance == ally:
                            change.oldalliance = other
                        if change.newalliance == ally:
                            change.newalliance = other
                        change.save()
                    ally.delete()

    def add_facwartopstats(self):
        api = apiroot()
        fwts = api.eve.FacWarTopStats()
        charids = set()
        for row in (list(fwts.characters.KillsYesterday) +
                    list(fwts.characters.KillsLastWeek) +
                    list(fwts.characters.KillsTotal) +
                    list(fwts.characters.VictoryPointsYesterday) +
                    list(fwts.characters.VictoryPointsLastWeek) +
                    list(fwts.characters.VictoryPointsTotal)):
            charids.add(row.characterID)
        corpids = set()
        for row in (list(fwts.corporations.KillsYesterday) +
                    list(fwts.corporations.KillsLastWeek) +
                    list(fwts.corporations.KillsTotal) +
                    list(fwts.corporations.VictoryPointsYesterday) +
                    list(fwts.corporations.VictoryPointsLastWeek) +
                    list(fwts.corporations.VictoryPointsTotal)):
            corpids.add(row.corporationID)
        for charid in charids:
            Pilot.objects.get_or_create(characterid=charid)
        for corpid in corpids:
            Corporation.objects.get_or_create(corporationid=corpid)

    def update_alliances(self):
        api = apiroot()
        allyapi = api.eve.AllianceList()
        lastapi = datetime.datetime.utcfromtimestamp(
            allyapi._meta.currentTime)
        for allyinfo in allyapi.alliances:
            ally, created = Alliance.objects.get_or_create(
                allianceid=allyinfo.allianceID)
            ally.update_intel(
                lastapi,
                name=allyinfo.name,
                ticker=allyinfo.shortName,
                members=allyinfo.memberCount,
                active=True,
                lastapi=lastapi,
                )
        for ally in Alliance.objects.filter(lastapi__lt=lastapi,
                                            active=True):
            ally.active = False
            ally.save()
        connection._commit()

    def update_standings(self):
        c = connection.cursor()
        c.execute("UPDATE intel_corporation SET standing = NULL")
        c.execute("UPDATE intel_alliance SET standing = NULL")
        for itemid, standing in get_standings().items():
            try:
                corp = Corporation.objects.get(corporationid=itemid)
                corp.standing = standing
                corp.save()
            except Corporation.DoesNotExist:
                pass
            try:
                ally = Alliance.objects.get(allianceid=itemid)
                ally.standing = standing
                ally.save()
            except Alliance.DoesNotExist:
                pass
        connection._commit()

    def collect_agenda(self):
        agenda = set()
        for pilot in Pilot.objects.filter(lastapi=None):
            agenda.add(('pilot', pilot.characterid))
        for corp in Corporation.objects.filter(
            active=True,
            lastapi__lt=datetime.datetime.now() - datetime.timedelta(days=1)
            ).filter(
            Q(lastapi=None) |
            ~Q(standing=None) |
            Q(faction__name='Amarr Empire')):

            agenda.add(('corp', corp.corporationid))
        # FIXME!
        # Support tracking
        # - tracked alliances
        # - tracked corps and corps in tracked alliances
        # - tracked pilots and pilots in tracked corps / alliances
        return sorted(agenda)

    def check(self, entity):
        (entitytype, itemid) = entity
        if entitytype == 'pilot':
            self.check_pilot(itemid)
        elif entitytype == 'corp':
            self.check_corp(itemid)

    def check_pilot(self, itemid):
        pilot = Pilot.objects.get(characterid=itemid)
        if not pilot.active:
            return
        if not (3000000 <= itemid < 4000000 or # NPCs
                90000000 <= itemid < 98000000 or # Old player characters
                100000000 <= itemid): # New player characts
            # Bad itemID!
            logging.info("Deleting pilot %s (bad itemID %s)" %
                         (pilot.name, itemid))
            pilot.kill_set.clear()
            pilot.delete()
            connection._commit()
            return
        api = apiroot()
        try:
            charinfo = api.eve.CharacterInfo(characterID=itemid)
        except eveapi.Error as e:
            logging.info("Pilot %s - API error %s: %s" %
                         (itemid, e.code, str(e)))
            if e.code in (105, 522): # Invalid characterID
                pilot.active = False
                pilot.save()
                connection._commit()
            return
        except:
            logging.exception("Exception during pilot check")
            return
        corp, created = Corporation.objects.get_or_create(
            corporationid=charinfo.corporationID)
        if hasattr(charinfo, 'allianceID'):
            ally, created = Alliance.objects.get_or_create(
                allianceid=charinfo.allianceID)
        else:
            ally = None
        lastapi = datetime.datetime.utcfromtimestamp(
            charinfo._meta.currentTime)
        pilot.update_intel(
            lastapi,
            name=charinfo.characterName,
            corporation=corp,
            alliance=ally,
            security=charinfo.securityStatus,
            lastapi=lastapi,
            )
        connection._commit()

    def check_corp(self, itemid):
        corp = Corporation.objects.get(corporationid=itemid)
        if not corp.active:
            return
        if not (1000000 <= itemid < 2000000 or # NPC corps
                98000000 <= itemid < 99000000 or # Old player corps
                100000000 <= itemid): # New player corps
            # Bad itemID!
            logging.info("Deleting corporation %s (bad itemID %s)" %
                         (corp.name, itemid))
            corp.kill_set.clear()
            corp.delete()
            connection._commit()
            return
        api = apiroot()
        try:
            corpinfo = api.corp.CorporationSheet(corporationID=itemid)
        except eveapi.Error as e:
            logging.info("Corporation %s - API error %s: %s" %
                         (itemid, e.code, str(e)))
            if e.code == 523: # Failed getting corporation information
                corp.active = False
                corp.save()
                connection._commit()
            return
        except:
            logging.exception("Exception during corp check")
            return
        if hasattr(corpinfo, 'allianceID'):
            ally, created = Alliance.objects.get_or_create(
                allianceid=corpinfo.allianceID)
        else:
            ally = None
        lastapi = datetime.datetime.utcfromtimestamp(
            corpinfo._meta.currentTime)
        corp.update_intel(
            lastapi,
            name=corpinfo.corporationName,
            alliance=ally,
            ticker=corpinfo.ticker,
            members=corpinfo.memberCount,
            lastapi=lastapi
            )
        connection._commit()
