import logging
import threading
import time
import Queue

from cobe.brain import Brain

class Chatter(threading.Thread):
    def __init__(self, bot):
        super(Chatter, self).__init__()
        self.daemon = True
        self.status = "Starting up"
        self.bot = bot
        self.q = Queue.Queue()
        self.brain = None
        logger = logging.getLogger('cobe')
        logger.setLevel(logging.INFO)

    def handle_being_addressed(self, nick, reply, text):
        self.q.put(('reply', nick, reply, text))

    def learn(self, text):
        self.q.put(('learn', text))

    def run(self):
        try:
            self.brain = Brain(self.bot.ctrl.conf.get('irc', 'brain'))
        except:
            logging.exception("Exception during brain initialization")
            raise
        while True:
            try:
                self.run2()
            except:
                logging.exception("Exception during Chatter.run2()")
                time.sleep(60)

    def run2(self):
        while True:
            self.status = "Waiting for command"
            cmd = self.q.get()
            if cmd[0] == 'learn':
                self.status = "Learning"
                self.brain.learn(cmd[1])
            elif cmd[0] == 'reply':
                self.status = "Replying"
                nick = cmd[1]
                reply = cmd[2]
                text = cmd[3]
                reply_text = self.brain.reply(text)
                reply("%s: %s" % (nick, reply_text))
