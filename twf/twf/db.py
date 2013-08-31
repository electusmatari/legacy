# db.py --- Database abstraction layer

# Copyright (C) 2010 Jorgen Schaefer <forcer@forcix.cx>

__all__ = ["cursor", "W"]

from futil import Table

from config import config

DBHANDLER = {}

_databases = {}
def cursor(dbname):
    """
    Return a TableCursor for the given database.

    This could at some point implement connectionpooling for threads,
    but as of now, it does not.
    """
    if dbname not in _databases:
        dbmodule = config.get(dbname, "module")
        Handler = DBHANDLER.get(dbmodule, DBBaseConnection)
        conn = Handler(**dict((name, value) for (name, value)
                              in config.items(dbname)))
        _databases[dbname] = conn
    return _databases[dbname].cursor()

class DBBaseConnection(object):
    def __init__(self, module, **kwargs):
        self.module = __import__(module)
        self.connection = self.module.connect(**kwargs)

    def close(self):
        """
        Close the connection.
        """
        self.connection.close()

    def commit(self):
        """
        Commit any pending transactions.
        """
        self.connection.commit()

    def rollback(self):
        """
        Roll back to the start of the pending transaction.
        """
        self.connection.rollback()

    def cursor(self):
        """
        Return a TableCursor for this connection.
        """
        return TableCursor(self, self.connection.cursor())

    def literal(self, s):
        """
        Return a quoted literal string, e.g. table names.
        """
        return '"%s"' % (s.replace('"', '""'),)

class PgSQLConnection(DBBaseConnection):
    def cursor(self):
        """
        Return a TableCursor for this connection.
        """
        return PGTableCursor(self, self.connection.cursor())
DBHANDLER['psycopg2'] = PgSQLConnection

class MySQLConnection(DBBaseConnection):
    def __init__(self, *args, **kwargs):
        super(MySQLConnection, self).__init__(*args, **kwargs)
        c = self.cursor()
        c.execute("SET sql_mode = 'ANSI_QUOTES'")
        c.execute("SET time_zone = '+0:00'")
        c.execute("SET NAMES 'utf8'")
        c.close()
DBHANDLER['MySQLdb'] = MySQLConnection

class TableCursor(object):
    """
    A cursor object that returns tables instead of lists.
    """
    def __init__(self, connection, cursor):
        self.connection = connection
        self.cursor = cursor

    def insert(self, pk, fmt, args=()):
        """
        Execute an INSERT command and return the primary key of the new row.

        pk must be the column name of the primary key.
        """
        self.execute(fmt, args)
        return self.cursor.lastrowid

    def updatedict(self, table, pk, d):
        """
        Update the database with a dictionary.

        The dictionary gives a mapping of column names to values. The
        row with the same primary key (pk) is changed.
        """
        keys = d.keys()
        self.execute("UPDATE %s SET %s WHERE %s = %%s" %
                     (self.connection.literal(table),
                      ", ".join(["%s = %%s" % self.connection.literal(col)
                                 for col in keys]),
                      self.connection.literal(pk)),
                     [d[key] for key in keys] + [d[pk]])

    def insertdict(self, table, pk, d):
        """
        Insert a dictionary into the database.

        The dictionary gives a mapping of column names to values.

        Returns the primary key (pk) of the new row.
        """
        keys = d.keys()
        return self.insert(pk,
                           "INSERT INTO %s (%s) VALUES (%s)" %
                           (self.connection.literal(table),
                            ", ".join([self.connection.literal(col)
                                       for col in keys]),
                            ", ".join(["%s"] * len(keys))),
                           [d[key] for key in keys])

    @property
    def description(self):
        return self.cursor.description

    @property
    def rowcount(self):
        return self.cursor.rowcount

    def callproc(self, procname, parameters=None):
        return self.cursor.callproc(procname, parameters)

    def close(self):
        self.cursor.close()

    def execute(self, operation, parameters=()):
        return self.cursor.execute(operation, parameters)

    def executemany(self, operation, seq_of_parameters):
        return self.cursor.executemany(operation, seq_of_parameters)

    def fetchone(self):
        return make_table(self.cursor, [self.cursor.fetchone()])[0]

    def fetchmany(self, size=None):
        return make_table(self.cursor, self.cursor.fetchmany(size))

    def fetchall(self):
        return make_table(self.cursor, self.cursor.fetchall())

    @property
    def arraysize(self):
        return self.cursor.arraysize

    @arraysize.setter
    def arraysize(self, value):
        self.cursor.arraysize = value

    def setinputsizes(self, sizes):
        self.cursor.setinputsizes(sizes)

    def setoutputsize(self, size, column=None):
        self.cursor.setoutputsize(size, column)

class PGTableCursor(TableCursor):
    def insert(self, pk, fmt, args=()):
        """
        Execute an INSERT command and return the primary key of the new row.

        pk must be the column name of the primary key.
        """
        self.execute("%s RETURNING %s" % (fmt, self.connection.literal(pk)),
                     args)
        return self.fetchone()[0]

def make_table(cursor, rows):
    """
    Create a new table from a dbapi cursor object and rows.

    cursor is a cursor object that just performed a successful
    execute() call.

    rows is the result of the cursor.fetch*() call.
    """
    return Table([desc[0] for desc in cursor.description],
                 rows)

class W(object):
    """
    A class to encapsulate a WHERE query.

    Can be combined with &, | and ~.
    """
    def __init__(self, fmt, args=[]):
        """
        Create a new W object.

        fmt is the format string to use.
        args is a list of arguments to pass to the formatter.
        """
        self.fmt = fmt
        self.args = args

    def __repr__(self):
        return "<W %r, %r>" % (self.fmt, self.args)

    def __str__(self):
        return self.fmt

    def notop(self, w):
        return W("(NOT (%s))" % (self.fmt,),
                 self.args)

    def dual(self, op, w):
        return W("((%s) %s (%s))" % (self.fmt, op, w.fmt),
                 self.args + w.args)

    def andop(self, w):
        return self.dual("AND", w)

    def orop(self, w):
        return self.dual("OR", w)

    def __invert__(self):
        return self.notop(self)
    def __and__(self, w):
        return self.andop(w)
    def __or__(self, w):
        return self.orop(w)
