#!/usr/bin/env python

import cgitb ; cgitb.enable()

import ConfigParser
import datetime
import os
import subprocess

BACKUPDIR = '/home/forcer/Projects/old-emcom/backup/'

def main():
    print "Content-Type: text/plain"
    print
    start = datetime.datetime.utcnow()
    cfg = ConfigParser.ConfigParser()
    cfg.read(['/home/forcer/Projects/old-emcom/kgi.cfg'])
    for sec in cfg.sections():
        try:
            if cfg.get(sec, "dbapi") != 'MySQLdb':
                continue
        except ConfigParser.NoSectionError:
            continue
        except ConfigParser.NoOptionError:
            continue
        host = cfg.get(sec, "host")
        user = cfg.get(sec, "user")
        passwd = cfg.get(sec, "passwd")
        db = cfg.get(sec, "db")
        timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d")
        fname = "%s-%s-%s-%s.sql.gz" % (timestamp, sec, host, db)
        backupfile = os.path.join(BACKUPDIR, fname)
        if os.path.exists(backupfile):
            print "Backup already exists: %s" % fname
            continue
        #print "Backing up to %s" % fname
        mysqldump = subprocess.Popen(["/usr/bin/mysqldump",
                                      "--host=%s" % host,
                                      "--user=%s" % user,
                                      "--password=%s" % passwd,
                                      db,
                                      ],
                                     stdout=subprocess.PIPE)
        f = file(backupfile, "w")
        gzip = subprocess.Popen(['/bin/gzip', '-9'],
                                stdin=mysqldump.stdout,
                                stdout=f,
                                stderr=subprocess.PIPE)
        (o, e) = gzip.communicate()
        if len(e) > 0:
            print "Error:"
            print e
            print
    end = datetime.datetime.utcnow()
    #print "Run time: %s seconds" % ((end - start).seconds)

if __name__ == '__main__':
    main()
