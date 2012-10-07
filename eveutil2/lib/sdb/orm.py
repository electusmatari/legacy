# Copyright (C) 2010 Jorgen Schaefer
# Author: Jorgen Schaefer <forcer@forcix.cx>

# ForeignSet(cls, colname, attributename=None)
# N2M(cls, attributename, colname, relationtable, thiscol, thatcol)

import sdb
import re
import weakref

defaultdb = None

def setdefaultdb(db):
    global defaultdb
    defaultdb = db

def commit(self):
    defaultdb.commit()

def rollback(self):
    defaultdb.rollback()

def cursor(self):
    return defaultdb.cursor()

def close(self):
    defaultdb.close()
    setdefaultdb(None)

class O(object):
    def __init__(self, operation=None, parameters=[], **kwargs):
        if operation is None:
            conjunction = []
            args = []
            for col, val in kwargs.items():
                conjunction.append("%s = %%s" % (col,))
                args.append(val)
            self.operation = " AND ".join(conjunction)
            self.parameters = args
        elif isinstance(operation, basestring):
            self.operation = operation
            if isinstance(parameters, tuple):
                parameters = list(parameters)
            self.parameters = parameters
        elif isinstance(operation, (tuple, list)):
            self.operation = "(%s)" % (", ".join(["%s"] * len(operation)))
            self.parameters = operation
        else:
            raise RuntimeError("Unknown argument type to O: %s" % (operation,))

    def __repr__(self):
        return "<O %r %% %r>" % (self.operation, self.parameters)

    def __iter__(self):
        yield self.operation
        yield self.parameters

    def __add__(self, other):
        if isinstance(other, O):
            return O(self.operation + other.operation,
                     self.parameters + other.parameters)
        else:
            return O(self.operation + str(other),
                     self.parameters)

    def __radd__(self, other):
        if isinstance(other, O):
            return O(other.operation + self.operation,
                     other.parameters + self.parameters)
        else:
            return O(str(other) + self.operation,
                     self.parameters)

    def __and__(self, other):
        if other.operation == '':
            return self
        elif self.operation == '':
            return other
        else:
            return "((" + self + ") AND (" + other + "))"

    def __or__(self, other):
        if other.operation == '':
            return self
        elif self.operation == '':
            return other
        else:
            return "((" + self + ") OR (" + other + "))"

UPPER_RX = re.compile("([A-Z])")
def tablename(s):
    """
    Return the SQL table name for a class name.

    FooBar => foo_bar
    """
    return UPPER_RX.sub("_\\1", s).strip("_").lower()

class MetaDBTable(type):
    def __new__(meta, classname, bases, classdict):
        if 'Meta' not in classdict:
            classdict['Meta'] = type('Meta', (object,),
                                     {'table': tablename(classname),
                                      'pk': 'id'})
        if not hasattr(classdict['Meta'], 'table'):
            setattr(classdict['Meta'], 'table', tablename(classname))
        if not hasattr(classdict['Meta'], 'pk'):
            setattr(classdict['Meta'], 'pk', 'id')
        return type.__new__(meta, classname, bases, classdict)

class DBTable(sdb.DBRow):
    __metaclass__ = MetaDBTable

    @classmethod
    def get(cls, *args, **kwargs):
        if len(args) == 1:
            if isinstance(args[0], O):
                where = args[0]
            else:
                where = O("%s = %%s" % cls.Meta.pk,
                          [args[0]])
        elif len(args) > 1:
            raise TypeError("get() takes exactly 1 argument (%s given)"
                            % len(args))
        else:
            where = O(**kwargs)
        c = defaultdb.cursor()
        c.execute("SELECT * FROM %s WHERE %s" %
                  (cls.Meta.table, where.operation),
                  where.parameters)
        if c.rowcount == 0:
            raise sdb.DataError("Object does not exist (%r)" % (where,))
        elif c.rowcount > 1:
            raise sdb.DataError("More than one object found (%r)" % (where,))
        else:
            return c.fetchone(cls)

    @classmethod
    def filter(cls, *args, **kwargs):
        if len(args) == 1:
            where = args[0]
        elif len(args) > 1:
            raise TypeError("filter() takes exactly 1 argument (%s given)"
                            % len(args))
        else:
            where = O(**kwargs)
        c = defaultdb.cursor()
        c.execute("SELECT * FROM %s WHERE %s" %
                  (cls.Meta.table, where.operation),
                  where.parameters)
        return c.fetchall(cls)

class ForeignKey(object):
    def __init__(self, cls, attributename=None, colname=None):
        if attributename is None:
            attributename = cls.Meta.table + "_id"
        if colname is None:
            colname = cls.Meta.pk
        self.cls = cls
        self.attributename = attributename
        self.colname = colname
        self.cache = weakref.WeakKeyDictionary()

    def __get__(self, obj, objtype):
        if obj not in self.cache:
            self.cache[obj] = self.cls.get(**{
                    self.colname: getattr(obj, self.attributename)})
        return self.cache[obj]
