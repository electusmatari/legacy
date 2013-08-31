# futil.py --- forcer's utility functions

# Copyright (C) 2010 Jorgen Schaefer <forcer@forcix.cx>

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE FREEBSD PROJECT ``AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE FREEBSD PROJECT OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
# USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
# OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.

__all__ = ["Table", "Header", "Row", "AttributeDict"]

class Table(list):
    """
    A table is a list of rows.

    It's like a normal list, except it provides a simple way to create
    list of rows, and you can do an item lookup on it.
    """
    def __init__(self, arg1, arg2=None):
        """
        Return a new table.

        When called with one argument, that argument is a list to
        translate to a table.

        When called with two arguments, the first is a header tuple
        and the second a list of row tuples.
        """
        if arg2 is None:
            super(Table, self).__init__(arg1)
        else:
            h = Header(arg1)
            super(Table, self).__init__([Row(h, row) for row in arg2])

    def lookup(self, func):
        """
        Return the first element in lis for which func returns a true value.
        """
        for elt in self:
            if func(elt):
                return elt
        raise KeyError("Predicate did not find an element")

class Header(object):
    """
    A header stores column names.

    This is used by Rows to find the index of named fields.
    """
    def __init__(self, colnames):
        self.colnames = colnames
        self.col2index = dict(zip(colnames, range(len(colnames))))

    def index(self, colname):
        return self.col2index[colname]

class Row(tuple):
    """
    A Row is a tuple which can be accessed by named fields.

    This is implemented using indirection, not via
    collections.namedtuple, to allow for arbitrary field names.
    """
    def __new__(cls, header, values):
        self = super(Row, cls).__new__(cls, values)
        self._header = header
        return self

    def __repr__(self):
        return "<Row %s>" % (", ".join(["%s: %r" % (key, value)
                                        for (key, value)
                                        in zip(self._header.colnames,
                                               self)]))

    def __getattr__(self, name):
        return self[self._header.index(name)]

    def __getitem__(self, item):
        try:
            return super(Row, self).__getitem__(item)
        except TypeError:
            return super(Row, self).__getitem__(self._header.index(item))

    def get(self, i, default=None):
        """
        R.get(k[,d]) -> D[k] if k in D, else d.  d defaults to None.
        """
        if i in self._defaultdict or i < len(self):
            return self[i]
        else:
            return default

    def asdict(self):
        """
        Return the tuple as a dictionary, mapping field names to values.
        """
        return dict(zip(self._header.colnames, self))

    def asadict(self):
        """
        Return the tuple as a dictionary, mapping field names to values.
        """
        return AttributeDict(self.asdict())

class AttributeDict(dict):
    """
    An AttributeDict is a dictionary whose fields can be accessed as
    attributes.
    """
    def __repr__(self):
        return "<%s %s>" % (self.__class__.__name__,
                            super(AttributeDict, self).__repr__(),)

    def __getattr__(self, name):
        try:
            return super(AttributeDict, self).__getattr__(name)
        except AttributeError:
            return self[name]

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        del self[name]


# class Table(list):
#     """
#     A Table is a list of Rows.
# 
#     We provide some helper functions to utilize fast row access, too.
#     """
#     def __init__(self, header, rows=[]):
#         self._header = header
#         self._headerdict = dict(zip(header, range(len(header))))
#         super(Table, self).__init__([Row(self, row) for row in rows])
# 
#     def __repr__(self):
#         return "<%s %r with %i rows>" % (self.__class__.__name__,
#                                          self._header,
#                                          len(self))
# 
#     # Tables should be static. We can do some magic to keep a table a
#     # table, but in the end, it's a list, so just live with it turning
#     # into a list if you treat it like a list.
# 
#     # def __add__(self, b):
#     #     return Table(self._header,
#     #                  super(Table, self).__add__(b))
#     # 
#     # def __mul__(self, b):
#     #     return Table(self._header,
#     #                  super(Table, self).__mul__(b))
#     # 
#     # def append(self, row):
#     #     if isinstance(row, Row):
#     #         super(Table, self).append(row)
#     #     else:
#     #         super(Table, self).append(Row(self, row))
#     # 
#     # def extend(self, rows):
#     #     for row in rows:
#     #         self.append(row)
# 
#     def filter(self, predicate, fields=[]):
#         """
#         Return a Table with fewer arguments.
# 
#         The predicate is called with each element of the table, and
#         the values of the fields given in the fields argument. The
#         resulting table contains only elements for which the predicate
#         returned a true value.
#         """
#         if not hasattr(fields, "__iter__"):
#             fields = [fields]
#         indeces = [self._headerdict[field] for field in fields]
#         return Table(self._header,
#                      [elt for elt in self
#                       if predicate(elt, *[elt[i] for i in indeces])])
# 
#     def get(self, predicate, fields=[]):
#         """
#         Return a single row from the table.
# 
#         The predicate is called with each element of the table, and
#         the values of the fields given in the fields argument. The
#         first element for which this returns a true value is returned.
#         """
#         if not hasattr(fields, "__iter__"):
#             fields = [fields]
#         indeces = [self._headerdict[field] for field in fields]
#         for elt in self:
#             if predicate(elt, *[elt[i] for i in indeces]):
#                 return elt
#         raise KeyError("No element for this predicate found")
