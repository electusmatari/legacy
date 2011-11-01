import logging
import threading
import time

import feedparser

class FeedReader(threading.Thread):
    def __init__(self, conf, bot):
        super(FeedReader, self).__init__()
        self.daemon = True
        self.bot = bot
        self.feeds = []
        self.delay = conf.getint('feedfetcher', 'delay')
        for sec in conf.sections():
            if sec.lower().startswith("feed "):
                name = conf.get(sec, "name")
                url = conf.get(sec, "url")
                self.feeds.append((name, url))
        self.known = set()
        self.initialized = set()

    def run(self):
        while True:
            try:
                self.run2()
            except:
                logging.exception("Exception during feedfetcher run")
                time.sleep(600)

    def run2(self):
        while True:
            for name, url, entry in self.get_news():
                self.announce(name, url, entry)
            time.sleep(self.delay)

    def get_news(self):
        for name, url in self.feeds:
            try:
                feed = feedparser.parse(url)
            except Exception as e:
                logging.info("Error %s while fetching feed %s: %s" %
                             (e.__class__.__name__, name, str(e)))
                continue
            if url not in self.initialized:
                for entry in feed.entries:
                    self.known.add(entry.link)
                self.initialized.add(url)
                continue
            for entry in feed.entries:
                if entry.link not in self.known:
                    logging.info("link %r - known %r" %
                                 (entry.link, self.known))
                    self.known.add(entry.link)
                    yield (name, url, entry)

    def announce(self, name, url, entry):
        self.bot.broadcast("[%s] %s - %s" % (name, entry.title, entry.link))
