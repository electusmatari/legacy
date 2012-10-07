import logging
import socket
import threading
import time
import Queue

IRCPORT = 6667
PRIVMSGLEN = 400

class IRC(threading.Thread):
    flood_margin = 10
    flood_penalty = 3
    reconnect_delay = 1

    def __init__(self, address, nicklist, username=None, realname=None,
                 password=None):
        super(IRC, self).__init__()
        self.daemon = True
        self.log = logging.getLogger('irclib')

        if isinstance(address, tuple):
            self.address = address
        else:
            self.address = (address, IRCPORT)
        if isinstance(nicklist, basestring):
            self.nicklist = [nicklist]
        else:
            self.nicklist = nicklist
        if username is None:
            self.username = self.nicklist[0]
        else:
            self.username = username
        if realname is None:
            self.realname = "Python IRC Bot"
        else:
            self.realname = realname
        self.password = password
        self.sock = None
        self.sender = None
        self.is_running = False
        self.last_message = 0
        self.buf = ""

    def run(self):
        self.serve_forever()

    def stop(self, message="Departing"):
        self.is_running = False
        self.send_quit(message)
        self.disconnect()

    def serve_forever(self):
        self.is_running = True
        while self.is_running:
            try:
                if self.sender is not None:
                    self.sender.stop()
                self.connect()
                self.setup_sender()
                self.register()
                while self.is_running:
                    self.handle_irc_protocol(self.read_irc_protocol())
                self.disconnect()
            except Disconnected:
                if self.is_running:
                    self.log.warning("Disconnected, reconnecting")
                time.sleep(self.reconnect_delay)
            except OSError:
                self.log.warning("Connection problem during serve_forever")
            except Exception:
                self.log.exception("Exception in serve_forever")
                time.sleep(self.reconnect_delay)

    def connect(self):
        self.sock = socket.create_connection(self.address)

    def setup_sender(self):
        self.sender = Sender(self)
        self.sender.start()

    def register(self):
        if self.password is not None:
            self.send_pass(self.password)
        self.send_nick(self.nicklist[0])
        self.send_user(self.username, self.realname)

    def read_irc_protocol(self):
        while "\n" not in self.buf:
            new = self.sock.recv(4096)
            if new == '':
                raise Disconnected('EOF from server')
            self.buf += new
        idx = self.buf.index("\n")
        message = IRCMessage.parse(self.buf[:idx])
        self.buf = self.buf[idx + 1:]
        return message

    def handle_irc_protocol(self, message):
        func = getattr(self, "on_%s" % message.command.lower(), None)
        if func is not None:
            try:
                func(message)
            except:
                self.log.exception("Exception during handling of %s" %
                                   message.command)
        else:
            self.unhandled(message)

    def disconnect(self):
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
            self.sock.close()
        except:
            pass

    def unhandled(self, message):
        pass

    def send(self, message, noqueue=False):
        if noqueue:
            self.sock.send("%s\n" % str(message))
            self.sender.last_message += self.flood_penalty
        else:
            self.sender.sendq.put(message)

    def send_pass(self, password):
        self.send(IRCMessage("PASS", args=[password]))

    def send_nick(self, nickname):
        self.send(IRCMessage("NICK", nickname))

    def send_user(self, user, realname, mode=8):
        self.send(IRCMessage("USER", user, mode, "*", realname))
    
    def send_quit(self, reason):
        self.send(IRCMessage("QUIT", reason))

    def send_join(self, channel):
        self.send(IRCMessage("JOIN", channel))

    def send_part(self, channel, reason):
        self.send(IRCMessage("PART", channel, reason))

    def send_privmsg(self, target, message, do_split=True):
        if len(message) > PRIVMSGLEN and do_split:
            for line in split_at_words(message, PRIVMSGLEN):
                self.send_privmsg(target, line, False)
        else:
            self.send(IRCMessage("PRIVMSG", target, message))

    def send_pong(self, argument):
        self.send(IRCMessage("PONG", argument),
                  True)

    def on_ping(self, msg):
        self.send_pong(msg.args[0])

class Sender(threading.Thread):
    def __init__(self, irc):
        super(Sender, self).__init__()
        self.daemon = True
        self.irc = irc
        self.sendq = Queue.Queue()
        self.is_running = True

    def run(self):
        """
        Flood protection. See RFC 2812, section 5.8.

        - If last_message is less than the current time, set equal
        - While last_message is less than now() + margin
          - send message
          - increase last_message by flood_penalty for each message
        """
        while True:
            msg = self.sendq.get()
            if not self.is_running:
                break
            now = time.time()
            if self.last_message < now:
                self.last_message = now
            if self.last_message >= now + self.irc.flood_margin:
                time.sleep(self.last_message - (now + self.irc.flood_margin))
            self.irc.send(msg, True)

    def stop(self):
        self.is_running = False
        self.sendq.put(None)


class IRCBot(IRC):
    def __init__(self, *args, **kwargs):
        super(IRCBot, self).__init__(*args, **kwargs)
        self.is_registered = False
        self.current_nick = False
        self.channels = set()
        self.wanted_channels = set()
        self.attempted_nick = 0

    def try_next_nick(self):
        self.attempted_nick += 1
        self.send_nick(self.nicklist[self.attempted_nick])

    def check_nick(self):
        if self.current_nick.lower() != self.nicklist[0].lower():
            self.send_nick(self.nicklist[0])

    def on_001(self, msg): # RPL_WELCOME
        self.is_registered = True
        self.current_nick = msg.args[0]
        for channel in self.wanted_channels:
            self.send_join(channel)

    def on_432(self, msg): # ERR_ERRONEUSNICKNAME
        if not self.is_registered:
            self.try_next_nick()

    def on_433(self, msg): # ERR_NICKNAMEINUSE
        if not self.is_registered:
            self.try_next_nick()

    def on_437(self, msg): # ERR_UNAVAILRESOURCE
        if not self.is_registered:
            self.try_next_nick()

    def on_join(self, msg):
        if irceq(msg.source.nick, self.current_nick):
            self.channels.add(msg.args[0].lower())

    def on_part(self, msg):
        if irceq(msg.source.nick, self.current_nick):
            channel = msg.args[0]
            self.channels.remove(channel.lower())
            if channel.lower() in self.wanted_channels:
                self.send_join(channel)

    def on_kick(self, msg):
        if irceq(msg.source.nick, self.current_nick):
            channel = msg.args[0]
            self.channels.remove(channel.lower())

    def on_privmsg(self, msg):
        if msg.args[0] == self.current_nick:
            reply_to = msg.source.nick
        else:
            reply_to = msg.args[0]
        self.handle_message(msg,
                            lambda text: self.send_privmsg(reply_to, text),
                            msg.args[1])
    
class IRCMessage(object):
    def __init__(self, command, *args):
        self.source = None
        self.command = command.upper()
        self.args = args or []

    def __str__(self):
        fragments = []
        if self.source is not None:
            fragments.append(":%s" % self.source)
        fragments.append(self.command)
        fragments.extend(self.args[:-1])
        if len(self.args) > 0:
            fragments.append(":%s" % self.args[-1])
        return " ".join(unicode(x).encode("utf-8") for x in fragments)

    def __repr__(self):
        return "<IRCMessage %s>" % str(self)

    @classmethod
    def parse(cls, commandstring):
        commandstring = commandstring.rstrip("\r")
        if commandstring.startswith(":"):
            try:
                idx = commandstring.index(" ")
            except ValueError:
                raise ParseError("Malformed message: Only a source given")
            source = commandstring[1:idx]
            commandstring = commandstring[idx + 1:]
        else:
            source = None
        try:
            idx = commandstring.index(" :")
        except ValueError:
            lastarg = None
        else:
            lastarg = commandstring[idx + 2:]
            commandstring = commandstring[:idx]
        args = commandstring.split()
        if len(args) == 0:
            raise ParseError("Malformed message: No command")
        command = args[0]
        args = args[1:]
        if lastarg is not None:
            args.append(lastarg)
        obj = cls(command, *args)
        obj.source = IRCMessageSource.parse(source)
        return obj

class IRCMessageSource(object):
    def __init__(self, nick, user=None, host=None):
        self.nick = nick
        self.user = user
        self.host = host

    def __str__(self):
        if self.user is not None:
            return "%s!%s@%s" % (self.nick, self.user, self.host)

    def __repr__(self):
        return "<IRCMessageSource %s>" % str(self)

    @classmethod
    def parse(cls, source):
        if source is None:
            return None
        try:
            idx1 = source.index("!")
            idx2 = source.index("@")
        except ValueError:
            return cls(source)
        else:
            return cls(source[:idx1],
                       source[idx1+1:idx2],
                       source[idx2+1:])

def irceq(a, b):
    return a.lower() == b.lower()

def split_at_words(text, length):
    while len(text) > length:
        wspace = text.rfind(" ", None, length)
        if wspace == -1:
            wspace = length
        yield text[:wspace]
        text = text[wspace+1:]
    yield text
    return

class Disconnected(Exception):
    pass

class ParseError(Exception):
    pass
