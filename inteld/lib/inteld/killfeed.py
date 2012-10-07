# Kill info feed reader

import datetime
import logging
import threading
import urllib
import time
import Queue

from django.db.models import Q
from django.db import connection, IntegrityError

from emtools.ccpeve.models import APIKey, apiroot
from emtools.intel.models import Feed, EDKFeed, Kill, EntityCache
from emtools.intel import killinfo

FETCHER = {}

# Yes, this does nothing in the run method.
class KillFeedFetcher(threading.Thread):
    def __init__(self, ctrl):
        super(KillFeedFetcher, self).__init__()
        self.daemon = True
        self.status = "Starting up"
        self.ctrl = ctrl
        self.feedq = Queue.Queue()
        self.evscofeedq = Queue.Queue()

        fg = FeedGenerator(self.feedq, self.evscofeedq, ctrl.stats)
        fg.start()

        nfeedreaderthreads = self.ctrl.conf.getint('killfeed',
                                                   'feedreaderthreads')
        for ff in range(nfeedreaderthreads):
            ff = FeedFetcher(self.feedq, ctrl.stats)
            ff.start()
        eff = FeedFetcher(self.evscofeedq, ctrl.stats)
        eff.start()

        iw = InvolvedWriter(ctrl.stats)
        iw.start()

        janitor = Janitor(ctrl.stats)
        janitor.start()

    def run(self):
        pass

class InvolvedWriter(threading.Thread):
    def __init__(self, stats):
        super(InvolvedWriter, self).__init__()
        self.daemon = True
        self.status = "Starting up"
        self.stats = stats

    def run(self):
        while True:
            try:
                self.run2()
            except:
                connection._rollback()
                logging.exception("Exception during InvolvedWriter run")
                time.sleep(60)

    def run2(self):
        while True:
            self.status = "Getting kill objects"
            ec = EntityCache()
            kill_list = list(Kill.objects.filter(involved_added=False))
            self.status = ("Adding involved parties to %s kills" %
                           len(kill_list))
            if len(kill_list) > 0:
                logging.debug("Adding involved parties to %s kills" %
                              len(kill_list))
            for kill in kill_list:
                try:
                    kill.add_involved(ec)
                except:
                    connection._rollback()
                    logging.exception("Exception during add_involved()")
                else:
                    connection._commit()
            connection._commit()
            self.status = "Waiting"
            time.sleep(60*5)


class FeedGenerator(threading.Thread):
    def __init__(self, feedq, evscofeedq, stats):
        super(FeedGenerator, self).__init__()
        self.daemon = True
        self.status = "Starting up"
        self.feedq = feedq
        self.evscofeedq = evscofeedq
        self.stats = stats

    def run(self):
        while True:
            try:
                self.run2()
            except:
                logging.exception("Exception during FeedGenerator run")
                time.sleep(60)

    def run2(self):
        while True:
            self.status = "Generating feeds"
            feed_list = self.get_feeds()
            evsco_feed_list = self.get_evsco_feeds()
            numfeeds = len(feed_list) + len(evsco_feed_list)
            self.status = "Fetching from %s feeds" % numfeeds
            if numfeeds > 0:
                logging.debug("Fetching from %s feeds" % numfeeds)
            for feed in feed_list:
                feed.lastchecked = datetime.datetime.utcnow()
                feed.save()
                self.feedq.put(feed)
            for feed in evsco_feed_list:
                feed.lastchecked = datetime.datetime.utcnow()
                feed.save()
                self.evscofeedq.put(feed)
            connection._commit()
            self.status = "Waiting"
            time.sleep(60*15)

    def get_feeds(self):
        result = []
        old = datetime.datetime.utcnow() - datetime.timedelta(hours=12)
        feedqs = Feed.objects.exclude(disabled=True)
        feedqs = feedqs.filter(Q(lastchecked=None) |
                               Q(lastchecked__lt=old))
        for feed in feedqs:
            result.append(feed)
        return result

    def get_evsco_feeds(self):
        key = APIKey.objects.get(name='Gradient')
        cl = key.corp().ContactList()
        api = apiroot()
        al = api.eve.AllianceList()
        all_alliances = set(a.allianceID for a in al.alliances)
        old = datetime.datetime.utcnow() - datetime.timedelta(hours=23)
        result = []
        for contact in cl.allianceContactList:
            if contact.contactID in all_alliances:
                feed, created = EDKFeed.objects.get_or_create(
                    allianceid=contact.contactID)
            else:
                feed, created = EDKFeed.objects.get_or_create(
                    corpid=contact.contactID)
            if feed.lastchecked is None or feed.lastchecked < old:
                result.append(feed)
        return result


class FeedFetcher(threading.Thread):
    def __init__(self, feedq, stats):
        super(FeedFetcher, self).__init__()
        self.daemon = True
        self.status = "Starting up"
        self.feedq = feedq
        self.stats = stats

    def run(self):
        while True:
            try:
                self.run2()
            except:
                logging.exception("Exception during FeedFetcher run")
                time.sleep(60)

    def run2(self):
        while True:
            self.status = "Waiting for feed job"
            feed = self.feedq.get()
            self.status = "Fetching from feed %s" % feed.url
            try:
                fetcher = FETCHER[feed.feedtype](feed)
                for kill in fetcher.fetch():
                    obj, created = Kill.objects.get_or_create_from_killinfo(
                        kill)
                    self.stats.numkills += 1
                    if created:
                        self.stats.numnewkills += 1
                feed.error = ""
                feed.failed_attempts = 0
                feed.save()
                connection._commit()
                self.stats.numfeeds += 1
                time.sleep(5)
            except Exception as e:
                connection._rollback()
                if not isinstance(e, (NoDataError, FeedParsingError)):
                    logging.info("Exception %s during fetching of feed %s: %s"
                                 % (e.__class__.__name__, feed.url, str(e)))
                feed.error = str(e)[:255]
                feed.failed_attempts += 1
                if feed.failed_attempts > 5:
                    feed.disabled = True
                    logging.info("Disabling feed %s" % feed.url)
                    self.stats.numfeeddisabled += 1
                feed.save()
                connection._commit()
                self.stats.numfeederrors += 1
                time.sleep(10)

class BaseFeed(object):
    def __init__(self, feed):
        self.feed = feed
        self.state = feed.state

    def fetch(self):
        if self.state is None:
            self.state = self.get_initial_state()
        while True:
            for kill in self.fetch_single():
                yield kill
            oldstate = self.feed.state
            self.feed.state = self.state
            self.feed.save()
            if self.state == oldstate:
                return
            time.sleep(1.5)

    def parse_page(self, **kwargs):
        if "?" in self.feed.url:
            url = self.feed.url + "&" + urllib.urlencode(kwargs)
        else:
            url = self.feed.url + "?" + urllib.urlencode(kwargs)
        data = None
        try:
            return self.parse(self.sanitize(self.retrieve_url(url)))
        except Exception as e:
            if data is None:
                logging.error("Can't parse document at %s - %s: %s" %
                              (url, e.__class__.__name__, str(e)))
            else:
                logging.error("Can't parse document at %s - %s: %s, "
                              "data was %r" %
                              (url, e.__class__.__name__, str(e), data[0:100]))
            raise FeedParsingError(e, url)

    def parse(self, data):
        raise RuntimeError("%s does not define a parse() method" %
                           self.__class__.__name__)

    def sanitize(self, data):
        return data

    def retrieve_url(self, url):
        try:
            if "eve-kill" in url:
                time.sleep(60*8) # Only once every 8 minutes
                logging.info("Retrieving %s" % url)
            return urllib.urlopen(url).read()
        except:
            if "eve-kill" not in url:
                raise
            else:
                time.sleep(5)
                return urllib.urlopen(url + "&try=2").read()


class IDFeedFetcher(BaseFeed):
    def fetch_single(self):
        args = {'allkills': 1,
                'lastintID': self.state}
        if 'eve-kill' in self.feed.url:
            ts = datetime.datetime.utcnow() - datetime.timedelta(days=56)
            startdate = int(time.mktime(ts.timetuple()))
            args['startdate'] = startdate
        for kill in self.parse_page(**args):
            yield kill
            self.state = max(self.state, kill.kill_internal_id)

    def get_initial_state(self):
        ts = datetime.datetime.utcnow() - datetime.timedelta(days=56)
        startdate = int(time.mktime(ts.timetuple()))
        try:
            newstate = None
            for kill in self.parse_page(allkills=1, startdate=startdate):
                if newstate is None:
                    kill.kill_internal_id
                else:
                    newstate = min(newstate, kill.kill_internal_id)
            return newstate
        except NoDataError:
            pass
        ts = datetime.datetime.utcnow() - datetime.timedelta(days=7)
        startdate = int(time.mktime(ts.timetuple()))
        try:
            newstate = None
            for kill in self.parse_page(allkills=1, startdate=startdate):
                if newstate is None:
                    kill.kill_internal_id
                else:
                    newstate = min(newstate, kill.kill_internal_id)
            return newstate
        except NoDataError:
            pass
        try:
            newstate = None
            for kill in self.parse_page(allkills=1):
                if newstate is None:
                    kill.kill_internal_id
                else:
                    newstate = min(newstate, kill.kill_internal_id)
            return newstate
        except NoDataError:
            raise
        raise RuntimeError("Can't fetch initial state")

    def sanitize(self, data):
        try:
            start = data.index("<eveapi")
            end = data.index("</eveapi>") + len("</eveapi>")
        except ValueError:
            raise NoDataError(data)
        return data[start:end]

    def parse(self, data):
        return killinfo.parse_api_page(data)

FETCHER['idfeed'] = IDFeedFetcher


class NoDataError(Exception):
    def __init__(self, data):
        super(NoDataError, self).__init__("Only got: %r" % (data[:200],))

class FeedParsingError(Exception):
    def __init__(self, error, url):
        super(FeedParsingError, self).__init__(
            "Can't parse document at %s: %s" % (url, str(error)))
        self.parent_error = error
        self.url = url

class Janitor(threading.Thread):
    def __init__(self, stats):
        super(Janitor, self).__init__()
        self.daemon = True
        self.status = "Starting up"
        self.stats = stats

    def run(self):
        try:
            self.run2()
        except:
            logging.exception("Exception during Janitor run")
            time.sleep(600)

    def run2(self):
        while True:
            self.status = "Cleaning kills"
            self.clean_kills()
            self.status = "Waiting"
            time.sleep(60*60*12)
            
    def clean_kills(self):
        old = datetime.datetime.now() - datetime.timedelta(days=28*3)
        c = connection.cursor()
        c.execute("DELETE FROM intel_kill_involvedpilots inv "
                  "WHERE (SELECT timestamp FROM intel_kill "
                  "       WHERE intel_kill.id = inv.kill_id "
                  "      ) < %s",
                  (old,))
        c.execute("DELETE FROM intel_kill_involvedcorps inv "
                  "WHERE (SELECT timestamp FROM intel_kill "
                  "       WHERE intel_kill.id = inv.kill_id "
                  "      ) < %s",
                  (old,))
        c.execute("DELETE FROM intel_kill_involvedalliances inv "
                  "WHERE (SELECT timestamp FROM intel_kill "
                  "       WHERE intel_kill.id = inv.kill_id "
                  "      ) < %s",
                  (old,))
        c.execute("DELETE FROM intel_kill_involvedfactions inv "
                  "WHERE (SELECT timestamp FROM intel_kill "
                  "       WHERE intel_kill.id = inv.kill_id "
                  "      ) < %s",
                  (old,))
        c.execute("DELETE FROM intel_kill WHERE timestamp < %s",
                  (old,))
        ndeleted = c.rowcount
        try:
            connection._commit()
        except IntegrityError:
            connection._rollback()
            logging.info("Deletion of %i kills deferred due to parallel "
                         "kill feed fetching" % ndeleted)
        else:
            logging.info("Deleted %i kills" % ndeleted)
            self.stats.numkillsdeleted += ndeleted
