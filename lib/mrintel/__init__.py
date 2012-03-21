import irclib
import mrintel.eve.commands as evecommands

class MrIntel(irclib.IRCBot, evecommands.EVEBotMixIn):
    version = "MrIntel, your friendly neighborhood intelligence officer"

    def __init__(self, conf, server, port, nick, user, realname, channels):
        super(MrIntel, self).__init__(server, port, nick, user, realname,
                                      channels)
        self.conf = conf

    def on_ctcp_ACTION(self, sender, target, args):
        if args.startswith('pats {0}'.format(self.mynick)):
            if target is None:
                self.ctcp(sender.nick, "ACTION", "beams.")
            else:
                self.ctcp(target, "ACTION", "beams.")

    def on_ctcp_VERSION(self, sender, target, args=None):
        self.ctcp_reply(sender.nick, "VERSION", self.version)

    def cmd_STATUS(self, sender, channel):
        """
        Report some current stats about the bot.
        """
        import threading
        self.reply(sender, channel,
                   "I'm doing ok (running {nthreads} threads)."
                   .format(nthreads=threading.active_count()))

    def cmd_JOIN(self, sender, channel, target):
        """
        Make MrIntel join a given channel.
        """
        self.join_channel(target)
        self.msg(target, "Hello! {0} asked me to join here. Just use "
                 "{1}part to get rid of me.".format(sender.nick,
                                                    self.command_char))

    def cmd_PART(self, sender, channel):
        """
        Ask MrIntel to leave the current channel.
        """
        if channel is None:
            self.reply(sender, channel,
                       "Use the PART command in a channel, not in a query")
        else:
            self.part_channel(channel)
