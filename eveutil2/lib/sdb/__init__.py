# Copyright (C) 2010 Jorgen Schaefer
# Author: Jorgen Schaefer <forcer@forcix.cx>

import datetime
import exceptions
import re
import threading
import time
import weakref

__all__ = ['apilevel', 'threadsafety', 'paramstyle',
           'connect', 'Date', 'Time', 'Timestamp',
           'DateFromTicks', 'TimeFromTicks', 'TimestampFromTicks',
           'STRING', 'BINARY', 'NUMBER', 'DATETIME', 'ROWID',
           'Error', 'Warning', 'InterfaceError', 'DatabaseError',
           'InternalError', 'OperationalError', 'ProgrammingError',
           'IntegrityError', 'DataError', 'NotSupportedError']

apilevel = '2.0'
threadsafety = 2
paramstyle = 'format'

def connect(dbapi, **kwargs):
    """
    Connect to a DB-API database.

    dbapi is the DB-API 2.0 compatible module. Use further keyword
    arguments to pass them to the connect method of that backend.
    """
    if dbapi.apilevel != '2.0':
        raise IntegrityError("DB-API module apilevel %s is not supported"
                             % dbapi.apilevel)
    if dbapi.threadsafety < 1:
        raise InterfaceError("DB-API module is not threadsafe")
    if dbapi.paramstyle not in ('format', 'pyformat'):
        raise InterfaceError("DB-API module uses the wrong param style (%s)"
                             % dbapi.paramstyle)
    return DBConnection(dbapi, kwargs)

class DBRow(object):
    def __init__(self, header, values):
        self._header = header
        self._values = values

    def __repr__(self):
        fields = self._header.items()
        fields.sort(lambda a, b: cmp(a[1], b[1]))
        return "<%s %s>" % (self.__class__.__name__,
                            ", ".join("%s=%r" % (k, self[k])
                                      for (k, i) in fields))

    def __getitem__(self, name):
        if isinstance(name, int):
            return self._values[name]
        else:
            return self._values[self._header[name]]

    def __getattr__(self, name):
        return self[name]

    def __len__(self):
        return len(self._values)

class DBConnection(threading.local):
    """
    A database connection.

    This is a thread-local value, so a new connection is created for
    each thread it is used in.
    """
    def __init__(self, dbapi, kwargs):
        self.dbapi = dbapi
        with ExceptionProxy(self.dbapi):
            self.connection = dbapi.connect(**kwargs)

    def commit(self):
        """
        Commit the current transaction.
        """
        with ExceptionProxy(self.dbapi):
            self.connection.commit()

    def rollback(self):
        """
        Cause a rollback of the current transaction.
        """
        with ExceptionProxy(self.dbapi):
            self.connection.rollback()

    def cursor(self):
        """
        Return a cursor object for this connection.
        """
        return DBCursor(self)

    def close(self):
        """
        Close this database connection.
        """
        with ExceptionProxy(self.dbapi):
            self.connection.close()

class DBCursor(object):
    """
    A database cursor.
    """
    def __init__(self, connection):
        self.connection = connection
        with ExceptionProxy(self.connection.dbapi):
            self.cursor = connection.connection.cursor()
        self._lastheader = None

    def _header(self):
        if self._lastheader is None:
            self._lastheader = make_header(self.cursor)
        return self._lastheader

    @property
    def description(self):
        with ExceptionProxy(self.connection.dbapi):
            return [(name, DBTypeWrapper(self.connection.dbapi, type_code),
                     display_size, internal_size, precision, scale, null_ok)
                    for (name, type_code, display_size, internal_size,
                         precision, scale, null_ok)
                    in self.cursor.description]

    @property
    def rowcount(self):
        with ExceptionProxy(self.connection.dbapi):
            return self.cursor.rowcount

    def callproc(self, procname, *args, **kwargs):
        self._lastheader = None
        with ExceptionProxy(self.connection.dbapi):
            return self.cursor.callproc(procname, *args, **kwargs)

    def close(self):
        self._lastheader = None
        with ExceptionProxy(self.connection.dbapi):
            self.cursor.close()

    def execute(self, operation, parameters=()):
        self._lastheader = None
        with ExceptionProxy(self.connection.dbapi):
            self.cursor.execute(operation, parameters)

    def executemany(self, operation, seq_of_parameters):
        self._lastheader = None
        with ExceptionProxy(self.connection.dbapi):
            self.cursor.executemany(operation, seq_of_parameters)

    def fetchone(self, cls=DBRow):
        """
        Fetch the next row from the result set.

        If parent is given, the resulting object is a child of that
        class. Subsequent calls to fetch* will use the same parent
        object, even if a different one is given.
        """
        with ExceptionProxy(self.connection.dbapi):
            return cls(self._header(), self.cursor.fetchone())

    def fetchmany(self, size=None, cls=DBRow):
        """
        Return the size next rows from the result set.

        If parent is given, the resulting object is a child of that
        class. Subsequent calls to fetch* will use the same parent
        object, even if a different one is given.
        """
        if size is None:
            size = self.arraysize
        with ExceptionProxy(self.connection.dbapi):
            return [cls(self._header(), row)
                    for row in self.cursor.fetchmany(size)]

    def fetchall(self, cls=DBRow):
        """
        Return all rows in the result set.

        If parent is given, the resulting object is a child of that
        class. Subsequent calls to fetch* will use the same parent
        object, even if a different one is given.
        """
        with ExceptionProxy(self.connection.dbapi):
            return [cls(self._header(), row) for row in self.cursor.fetchall()]

    def nextset(self):
        with ExceptionProxy(self.connection.dbapi):
            return self.cursor.nextset()

    @property
    def arraysize(self):
        with ExceptionProxy(self.connection.dbapi):
            return self.cursor.arraysize

    def setinputsizes(self, sizes):
        with ExceptionProxy(self.connection.dbapi):
            self.cursor.setinputsize(sizes)

    def setoutputsizes(self, size, column=None):
        with ExceptionProxy(self.connection.dbapi):
            self.cursor.setoutputsizes(size, column)

def make_header(cursor):
    header = {}
    for i, description in enumerate(cursor.description):
        header[description[0]] = i
    return header

def Date(year, month, day):
    return datetime.date(year, month, day)

def Time(hour, minute, second):
    return datetime.time(hour, minute, second)

def Timestamp(year, month, day, hour, minute, second):
    return datetime.datetime(year, month, day, hour, minute, second)

def DateFromTicks(ticks):
    return Date(*time.localtime(ticks)[:3])

def TimeFromTicks(ticks):
    return Time(*time.localtime(ticks)[3:6])

def TimestampFromTicks(ticks):
    return Timestamp(*time.localtime(ticks)[:6])

class DBTypeWrapper(object):
    def __init__(self, dbapi, value):
        self.dbapi = dbapi
        self.value = value

    def __cmp__(self, other):
        return other.__cmp__(self)

class DBType(object):
    def __init__(self, name):
        self.name = name

    def __cmp__(self, other):
        if isinstance(other, DBTypeWrapper):
            if other.dbapi.__dict__[self.name] == other.value:
                return 0
            else:
                return 1
        elif isinstance(other, DBType):
            if self.name == other.name:
                return 0
            else:
                return 1
        else:
            return 1

STRING = DBType("STRING")
BINARY = DBType("BINARY")
NUMBER = DBType("NUMBER")
DATETIME = DBType("DATETIME")
ROWID = DBType("ROWID")

class Error(exceptions.StandardError):
    pass

class Warning(exceptions.StandardError):
    pass

class InterfaceError(Error):
    pass

class DatabaseError(Error):
    pass

class InternalError(DatabaseError):
    pass

class OperationalError(DatabaseError):
    pass

class ProgrammingError(DatabaseError):
    pass

class IntegrityError(DatabaseError):
    pass

class DataError(DatabaseError):
    pass

class NotSupportedError(DatabaseError):
    pass

class ExceptionProxy(object):
    exceptions = [('Error', Error),
                  ('Warning', Warning),
                  ('InterfaceError', InterfaceError),
                  ('DatabaseError', DatabaseError),
                  ('InternalError', InternalError),
                  ('OperationalError', OperationalError),
                  ('ProgrammingError', ProgrammingError),
                  ('IntegrityError', IntegrityError),
                  ('DataError', DataError),
                  ('NotSupportedError', NotSupportedError)]

    def __init__(self, dbapi):
        self.dbapi = dbapi

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            return False
        for (name, exception) in self.exceptions:
            if getattr(self.dbapi, name) == exc_type:
                raise exception(exc_value)
        return False
