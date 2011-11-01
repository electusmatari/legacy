import logging
import threading
import time

from emtools.ccpeve.models import APIKey
from inteld.utils import get_ownername

notificationTypeAllWarDeclaredMsg = 5
notificationTypeCorpWarDeclaredMsg = 27
notificationTypeCorpWarFightingLegalMsg = 28
notificationTypeAllWarSurrenderMsg = 6
notificationTypeCorpWarSurrenderMsg = 29
notificationTypeAllWarRetractedMsg = 7
notificationTypeCorpWarRetractedMsg = 30
notificationTypeAllWarInvalidatedMsg = 8
notificationTypeCorpWarInvalidatedMsg = 31

class NotificationWatcher(threading.Thread):
    FORMATS = {
        notificationTypeAllWarDeclaredMsg:
            "%(declaredByName)s has declared war on %(againstName)s",
        notificationTypeCorpWarDeclaredMsg:
            "%(declaredByName)s has declared war on %(againstName)s",
        notificationTypeCorpWarFightingLegalMsg:
            "%(declaredByName)s has declared war on %(againstName)s",
        notificationTypeAllWarSurrenderMsg:
            "%(againstName)s has surrendered to %(declaredByName)s",
        notificationTypeCorpWarSurrenderMsg:
            "%(againstName)s has surrendered to %(declaredByName)s",
        notificationTypeAllWarRetractedMsg:
            "%(declaredByName)s has retracted the war against %(againstName)s",
        notificationTypeCorpWarRetractedMsg:
            "%(declaredByName)s has retracted the war against %(againstName)s",
        notificationTypeAllWarInvalidatedMsg:
            "CONCORD invalidates the war declared by %(declaredByName)s against %(againstName)s because %(declaredByName)s forgot to pay the bribe",
        notificationTypeCorpWarInvalidatedMsg:
            "CONCORD invalidates the war declared by %(declaredByName)s against %(againstName)s because %(declaredByName)s forgot to pay the bribe"
        }

    def __init__(self, bot):
        super(NotificationWatcher, self).__init__()
        self.daemon = True
        self.key = APIKey.objects.get(name='Notifications').char()
        self.bot = bot
        self.known = set()
        self.initialized = False

    def run(self):
        while True:
            try:
                self.run2()
            except:
                logging.exception("Exception during NotificationWatcher run")
                time.sleep(600)

    def run2(self):
        while True:
            try:
                result = self.key.Notifications()
            except:
                time.sleep(600)
                continue
            for notif in result.notifications:
                if notif.notificationID in self.known:
                    continue
                if self.initialized and notif.typeID in self.FORMATS:
                    try:
                        textresult = self.key.NotificationTexts(
                            ids=notif.notificationID)
                    except:
                        continue
                    self.notify(notif.typeID,
                                parse_data(textresult.notifications[0].data))
                self.known.add(notif.notificationID)
            self.initialized = True
            time.sleep(result._meta.cachedUntil - time.time() + 1)

    def notify(self, typeid, argdict):
        fmt = self.FORMATS.get(typeid)
        if fmt is not None:
            self.bot.broadcast(fmt % argdict)

def parse_data(data):
    """
    Notifications have a text value that lists key/value pairs with
    one pair per line, like:

    againstID: <itemID>
    cost: 0
    declaredByID: <itemID>
    delayHours: 24
    hostileState: 0
    """
    result = {}
    for line in data.split("\n"):
        if line == '':
            continue
        if ": " not in line:
            logging.warning("Bad data format: %r" % (data,))
            continue
        key, value = line.split(": ", 1)
        try:
            value = int(value)
        except ValueError:
            pass
        result[key] = value

    if 'againstID' in result:
        result['againstName'] = get_ownername(result['againstID'])
    if 'declaredByID' in result:
        result['declaredByName'] = get_ownername(result['declaredByID'])
    return result
