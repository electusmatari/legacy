# MachoNet loader

import sys
sys.path.append("/home/forcer/Programs/Reverence/active/lib64/python2.6/site-packages/")

import os

from reverence import blue, dbutil, util

__all__ = ["load", "loadfile"]

def load(basedir):
    datafiles = listdir(os.path.join(basedir, "bulkdata"))
    try:
        macho = get_macho_directory(basedir)
    except OSError:
        macho = None
    if macho is not None:
        for dname in ['CachedObjects', 'CachedMethodCalls']:
            datafiles.extend(listdir(os.path.join(macho, dname)))
    data = {}
    for fname in datafiles:
        if fname.endswith(".cache2"):
            continue
        (name, obj) = loadfile(fname)
        if name not in data or obj.version > data[name].version:
            data[name] = obj
    return data
    
def loadfile(filename):
    try:
        (name, obj) = blue.marshal.Load(file(filename, "rb").read())
    except:
        print "Loading %s" % filename
        raise
    if type(name) == tuple and name[0] == 'Method Call':
        name = name[2]
    return (name, MachoObject(name, obj))

def get_macho_directory(basedir):
    serverdir = os.path.join(basedir, "cache", "MachoNet")
    servers = os.listdir(serverdir)
    if len(servers) > 1:
        sys.stderr.write("More than one server, using %s.\n" % servers[0])
    versiondir = os.path.join(serverdir, servers[0])
    version = max([int(x) for x in os.listdir(versiondir)])
    return os.path.join(versiondir, str(version))

def listdir(dirname):
    if os.path.isdir(dirname):
        return [os.path.join(dirname, fname)
                for fname in os.listdir(dirname)]
    else:
        return []

class MachoObject(object):
    def __init__(self, name, obj):
        self.name = name
        if type(obj) == dict and obj.has_key("lret"):
            self._origobj = obj
            self._obj = obj['lret']
            self.version = obj['version']
        else:
            self._origobj = obj
            self._obj = None
            self.version = getattr(obj, 'version', 0)

    def __repr__(self):
        return "<MachoObject %r>" % (self.name,)

    @property
    def obj(self):
        if self._obj is None:
            self._obj = self._origobj.GetObject()
        return self._obj

    def table(self):
        return macho2table(self.obj)

def macho2table(obj):
    guid = getattr(obj, "__guid__", None)
    if guid is not None:
        if guid.startswith("util.Row"):
            header, rows = obj.header, obj.lines
        elif guid.startswith("util.IndexRow"):
            header, rows = obj.header, obj.lines.values()
        elif guid == "dbutil.CRowset":
            header, rows = obj.header, obj
        elif guid == "dbutil.CIndexedRowset":
            header, rows = obj.header, obj.values()
        elif guid == "util.FilterRowset":
            header, rows = obj.header, list(obj.items.itervalues())
        elif guid == "blue.DBRow":
            header, rows = obj.__header__, [obj]
        elif guid == "util.KeyVal":
            keys = obj.__dict__.keys()
            header, rows = keys, [obj.__dict__[key] for key in keys]
        else:
            raise CoercionError("Unsupported cache type: %s" % guid)
    elif type(obj) == tuple and len(obj) == 2 and hasattr(obj[1], "__iter__"):
        header, rows = obj[0], obj[1]
    elif type(obj) == list and len(obj) > 0 and getattr(obj[0], "__guid__", None) == "blue.DBRow":
        header, rows = obj[0].__header__, obj
    elif type(obj) == dict:
        keys = obj.keys()
        header, rows = keys, [obj[key] for key in keys]
    else:
        raise CoercionError("Can't coerce to table: %s" % type(obj))
    if type(header) is blue.DBRowDescriptor:
        header = header.Keys()
    return Table(header, rows)

class Table(object):
    def __init__(self, header, rows):
        self.header = header
        self.name2idx = dict(zip(header, range(len(header))))
        self.rows = [Row(self, row) for row in rows]

    def __repr__(self):
        return "<Table with %s %s, header %r>" % (
            len(self.rows),
            "row" if len(self.rows) == 1 else "rows",
            self.header)

    def __iter__(self):
        for row in self.rows:
            yield row

    def __getitem__(self, i):
        return self.rows[i]

    def filter(self, column, value):
        t = Table(self.header, [])
        t.rows = [row for row in self.rows
                  if row[column] == value]
        return t

    def get(self, column, value):
        rows = [row for row in self.rows
                if row[column] == value]
        if len(rows) == 1:
            return rows[0]
        else:
            raise RuntimeError("More than one row found")

class Row(object):
    def __init__(self, table, row):
        self.table = table
        self.row = row

    def __repr__(self):
        return "<Row %s>" % (", ".join("%s: %r" % (a, b)
                                       for (a, b) in 
                                       zip(self.table.header, self.row)),)

    def __getattr__(self, name):
        return self[name]

    def __getitem__(self, i):
        return self.row[self.table.name2idx.get(i, i)]

    def get(self, i, default=None):
        if i in self.table.header or i < len(self.row):
            return self[i]
        else:
            return default

    def __iter__(self):
        for elt in self.row:
            yield elt

    def dict(self):
        return dict(zip(self.table.header, self.row))

class CoercionError(RuntimeError):
    pass

import datetime
def wintime_to_datetime(timestamp):
    return datetime.datetime.utcfromtimestamp(
        (timestamp - 116444736000000000L) / 10000000
        )
