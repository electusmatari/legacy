import logging
import Queue
import threading

from django.db import connection

from emtools.intel.models import TrackedEntity
from emtools.intel.models import Pilot, Corporation, Alliance

EVEWHO_DELAY = 35

class EVEWho(threading.Thread):
    def __init__(self, ctrl):
        super(EVEWho, self).__init__()
        self.daemon = True
        self.status = "Starting up"
        self.ctrl = ctrl
        self.q = Queue.Queue()
        self.checker = EVEWhoChecker(self.q, ctrl.stats)
        self.checker.start()

    def run(self):
        while True:
            try:
                self.run2()
            except:
                logging.exception("Exception during EVEWho run")
                time.sleep(60)

    def run2(self):
        last_put = 0
        last_get = time.time()
        while True:
            now = time.time()
            if (now - last_put) > 60*30: # Every 30 minutes:
                self.status = "Uploading information"
                self.put()
                connection._commit()
                last_put = now
            if (now - last_get) > 60*60*12: # Every 12h
                self.status = "Downloading information"
                self.fetch()
                connection._commit()
                last_get = now
            self.status = "Sleeping"
            time.sleep(60)

    def fetch(self):
        for te in TrackedEntity.objects.select_related(depth=1):
            if te.corporation is not None:
                self.q.put(te.corporation)
            if te.alliance is not None:
                self.q.put(te.alliance)

    def put(self):
        for pilot in Pilot.objects.filter(evewho=False):
            try:
                evewho_add(pilot.characterid)
                connection._commit()
            except:
                logging.exception("Exception during evewho_add()")
                time.sleep(60)
            else:
                pilot.evewho = True
                pilot.save()


class EVEWhoChecker(threading.Thread):
    def __init__(self, q, stats):
        super(EVEWhoChecker, self).__init__()
        self.daemon = True
        self.status = "Starting up"
        self.stats = stats
        self.q = q

    def run(self):
        while True:
            try:
                self.run2()
            except:
                logging.exception("Exception during EVEWhoCheck run")
                time.sleep(60)

    def run2(self):
        while True:
            self.status = "Waiting for jobs"
            entity = self.q.get()
            if entity.__class__.__name__ == 'Alliance':
                self.status = "Checking alliance %s" % entity.name
                self.add('allilist', entity.allianceid)
            elif entity.__class__.__name__ == 'Corporation':
                self.status = "Checking corp %s" % entity.name
                self.add('corplist', entity.corporationid)
            connection._commit()
            self.status = "Sleeping"
            time.sleep(EVEWHO_DELAY)

    def add(self, itemtype, itemid):
        character_ids = set()
        corporation_ids = set()
        alliance_ids = set()
        for row in evewhoapi(itemtype, itemid):
            character_ids.add(row['character_id'])
            corporation_ids.add(row['corporation_id'])
            alliance_ids.add(row['alliance_id'])
        for charid in character_ids:
            obj, created = Pilot.objects.get_or_create_from_api(
                characterid=charid)
            if not created:
                obj.apicheck()
            obj.evewho = True
            obj.save()
        for corpid in corporation_ids:
            obj, created = Corporation.objects.get_or_create_from_api(
                corporationid=corpid)
            if not created:
                obj.apicheck()
        for allianceid in alliance_ids:
            obj, created = Alliance.objects.get_or_create_from_api(
                allianceid=allianceid)
            if not created:
                obj.apicheck()

##################################################################
# Main EVE who connection

import json
import re
import time
import urllib

APIURL = "http://evewho.com/api.php"

THROTTLE_RX = re.compile(r'^hammering .* please wait ([0-9]+) seconds')

def evewhoapi(itemtype, itemid):
    args = {'type': itemtype,
            'id': itemid}
    result = []
    page = 0
    while True:
        url = APIURL + "?" + urllib.urlencode(args)
        while True:
            data = urllib.urlopen(url).read()
            m = THROTTLE_RX.match(data)
            if m is None:
                break
            time.sleep(int(m.group(1)) + 1)
        try:
            response = json.loads(data)
        except:
            raise EVEWhoError('Bad data from EVEWho API: %r' % data)
        result.extend(response['characters'])
        if len(response['characters']) == 0:
            return result
        page += 1
        args['page'] = page
        time.sleep(EVEWHO_DELAY)

ADDURL = "http://evewho.com/add.php"

def evewho_add(characterid):
    data = urllib.urlopen(ADDURL + ("?id=%s" % characterid)).read()
    if "Adding: " not in data:
        raise EVEWhoError("Couldn't add characterID %s: %r" %
                          (characterid, data))

class EVEWhoError(Exception):
    pass
