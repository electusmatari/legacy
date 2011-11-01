import datetime
import irclib
import shlex

from django.db import connection, connections

from emtools.ccpeve.models import apiroot

from inteld.bot.feedreader import FeedReader
from inteld.bot.changewatcher import ChangeWatcher
from inteld.bot.notificationwatcher import NotificationWatcher
from inteld.bot.commands.pricecheck import pricecheck
from inteld.bot.commands.info import info_npccorp, info_solarsystem
from inteld.bot.commands.info import info_apialliance, info_apicorp
from inteld.bot.commands.info import info_apichar
from inteld.bot.commands.route import find_route
from inteld.bot.silly import generate_reply
from inteld.bot.parser import getargs
from inteld.bot.error import CommandError
from inteld.utils import intcomma, floatcomma, sizestring, plural
from inteld.utils import get_itemid, get_ownerid

COMMANDCHAR = "!"

class MrIntel(irclib.IRCBot):
    def __init__(self, ctrl):
        self.ctrl = ctrl
        self.feedreader = FeedReader(ctrl.conf, self)
        self.feedreader.start()
        self.changewatcher = ChangeWatcher(self)
        self.changewatcher.start()
        self.notificationwatcher = NotificationWatcher(self)
        self.notificationwatcher.start()
        server = ctrl.conf.get('irc', 'server')
        if ":" in server:
            address = server.split(":")
            address[1] = int(address[1])
        else:
            address = (server, irclib.IRCPORT)
        nicks = [x.strip() for x in ctrl.conf.get('irc', 'nicks').split(",")]
        super(MrIntel, self).__init__(
            address, nicks,
            realname="http://www.youtube.com/watch?v=SOCDCcNSWhw")
        for channel in ctrl.conf.get('irc', 'channels').split(","):
            self.wanted_channels.add(channel.strip().lower())

    def handle_message(self, msg, reply, text):
        if text.lower().startswith('\x01action pats %s' %
                                    self.current_nick.lower()):
            reply("\x01ACTION beams.\x01")
        elif text.lower().startswith(self.current_nick.lower()):
            self.handle_text(msg, reply, text)
        elif text.startswith(COMMANDCHAR) and len(text) > 1:
            args = text.split(None, 1)
            cmd = args[0][1:]
            if len(args) > 1:
                args = args[1]
            else:
                args = ""
            func = getattr(self, "cmd_%s" % cmd.lower(), None)
            if func is None:
                reply("Unknown command '%s'" % cmd.lower())
            else:
                try:
                    func(msg, reply, args)
                except CommandError as e:
                    reply(str(e))
            connection._commit()

    def handle_text(self, msg, reply, text):
        try:
            idx = text.index(" ")
        except:
            return
        text = text[idx+1:].strip()
        reply("%s: %s" % (msg.source.nick,
                          generate_reply(text)))

    def broadcast(self, text):
        for chan in self.channels:
            self.send_privmsg(chan, text)

    def cmd_server(self, msg, reply, arg):
        import os
        st = os.statvfs("/")
        total = st.f_blocks * st.f_frsize
        free = st.f_bavail * st.f_bsize
        c = connection.cursor()
        c.execute("SELECT pg_database_size('eve')")
        (dbsize,) = c.fetchone()
        fc = connections['forum'].cursor()
        fc.execute("SELECT SUM(data_length + index_length) "
                   "FROM information_schema.TABLES")
        (mysqlsize,) = fc.fetchone()
        reply("%s / %s used, PostgreSQL database %s, MySQL database %s" %
              (sizestring(total - free), sizestring(total),
               sizestring(dbsize), sizestring(mysqlsize)))

    def cmd_pc(self, msg, reply, arg):
        typename, options = getargs(
            arg,
            {'region': 'Heimatar,Metropolis,Molden Heath,The Forge',
             'highsec': False})
        result = pricecheck(typename,
                            regions=options['region'].split(","),
                            highsec=options['highsec'])
        if 'system' in result:
            reply("%s for %s in %s, %s (%.1f)" %
                  (result['typename'], floatcomma(result['price']),
                   result['system'], result['region'], result['security']))
        elif 'price' in result:
            reply("%s for %s on contracts" %
                  (result['typename'], floatcomma(result['price'])))
        else:
            reply("Can't find a type matching '%s'" % typename)

    def cmd_info(self, msg, reply, arg):
        itemid = get_itemid(arg)
        if itemid is not None:
            crp = info_npccorp(itemid)
            if crp is not None:
                reply("%s is a non-capsuleer corp of the %s" %
                      (crp['name'], crp['faction']))
                return
            sys = info_solarsystem(itemid)
            if sys is not None:
                s = "%s, %s (%.1f" % (sys['name'],
                                       sys['region'],
                                       sys['security'])
                if 'kills' in sys:
                    s += ", %s kill%s" % (sys['kills'], plural(sys['kills']))
                
                s += "), %s sovereignty" % (sys['faction'] or "capsuleer",)
                if 'occupied' in sys:
                    s += ", occupied by the %s" % sys['occupied']
                if 'vp' in sys:
                    if sys['vp'] == 0:
                        s += ", not contested"
                    else:
                        s += ", contested with %s VP" % sys['vp']
                reply(s)
                return
        ownerid = get_ownerid(arg)
        if ownerid is not None:
            ally = info_apialliance(ownerid)
            if ally is not None:
                s = "%s <%s>" % (ally['name'], ally['ticker'])
                if ally['standing'] == 0:
                    s += " (neutral)"
                else:
                    s += " (%+i)" % ally['standing']
                s += ", %s member%s" % (ally['size'], plural(ally['size']))
                reply(s)
                return
            crp = info_apicorp(ownerid)
            if crp is not None:
                s = "%s [%s]" % (crp['name'], crp['ticker'])
                if crp['standing'] == 0:
                    s += " (neutral)"
                else:
                    s += " (%+i)" % crp['standing']
                s += ", %s member%s" % (crp['size'], plural(crp['size']))
                if crp['alliance']:
                    s += ", member of %s" % crp['alliance']
                    if crp['alliancestanding'] == 0:
                        s += " (neutral)"
                    else:
                        s += " (%+i)" % crp['alliancestanding']
                if crp['faction']:
                    s += ", member of the %s militia" % crp['faction']
                reply(s)
                return
            char = info_apichar(ownerid)
            if char is not None:
                s = ("%s (security %.1f), %s, member of %s" %
                     (char['name'], char['security'], char['bloodline'],
                      char['corp']))
                if char['corpstanding'] == 0:
                    s += " (neutral)"
                else:
                    s += " (%+i)" % char['corpstanding']
                if char['alliance']:
                    s += " / %s" % char['alliance']
                    if char['alliancestanding'] == 0:
                        s += " (neutral)"
                    else:
                        s += " (%+i)" % char['alliancestanding']
                if char['corpfaction']:
                    s += ", %s militia" % char['corpfaction']
                reply(s)
                return
        reply("I don't know what '%s' might be" % arg)

    def cmd_route(self, msg, reply, arg):
        routespec, options = getargs(
            arg,
            {'safer': False,
             'shorter': False,
             'avoid': ""})
        routelist = shlex.split(routespec)
        if len(routelist) != 2:
            reply("Please specify exactly two systems")
            return
        avoidlist = [x for x in options['avoid'].split(",")
                     if x != '']
        start = routelist[0].strip()
        end = routelist[1].strip()
        route = find_route(start, end, avoidlist, options['safer'])
        if route is None:
            reply("Can't find a route matching those criteria")
            return
        routedesc = []
        for name, sec in route:
            if sec < 0.0:
                color = "\x0304"
            elif sec < 0.45:
                color = "\x0307"
            else:
                color = "\x0303"
            routedesc.append("%s%s (%.1f)\x0f" %
                             (color, name, sec))
        reply("%s jumps: %s" % (len(route),
                                ", ".join(routedesc)))

    def cmd_tq(self, msg, reply, arg):
        api = apiroot()
        try:
            st = api.server.ServerStatus()
            ct = datetime.datetime.utcfromtimestamp(st._meta.currentTime)
            reply("Server %s, %s players [%s]" %
                  ("open" if st.serverOpen else "closed",
                   intcomma(st.onlinePlayers),
                   ct.strftime("%H:%M")))
        except Exception as e:
            reply("Error %s getting server status: %s" %
                  (e.__class__.__name__, str(e)))
