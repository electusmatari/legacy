import psycopg2
import MySQLdb

class Control(object):
    def __init__(self, conf):
        self.conf = conf
