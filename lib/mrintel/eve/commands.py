import logging
import threading

from mrintel.eve.api import EVEAPI
from mrintel.eve import pricecheck

class EVEBotMixIn(object):
    def defer_to_thread(self, target, sender, channel, *args):
        def handler():
            try:
                target(sender, channel, *args)
            except:
                self.reply(sender, channel, "I am terribly sorry, but "
                           "there was an error processing your command. "
                           "Admins have been notified.")
                logging.exception("Exception during {0}:".format(
                        target.__name__))
        t = threading.Thread(target=handler)
        t.daemon = True
        t.start()

    def cmd_TQ(self, sender, channel):
        """
        Return the current server status from the API.
        """
        self.defer_to_thread(self.thread_TQ, sender, channel)

    def thread_TQ(self, sender, channel):
        with EVEAPI(sender, channel) as apiroot:
            status = apiroot.server.ServerStatus()
            self.reply(sender, channel,
                       "Server {0}, {1:,} players online"
                       .format("open" if status.serverOpen == 'True'
                               else "closed",
                               status.onlinePlayers))

    def cmd_PC(self, sender, channel, typename):
        """
        Return a market quote for the given type name.
        """
        self.defer_to_thread(self.thread_PC, sender, channel, typename)
    cmd_PC.dont_parse_args = True

    def thread_PC(self, sender, channel, typename):
        price = pricecheck.pricecheck(typename)
        self.reply(sender, channel, pricecheck.format_reply(price, typename))
