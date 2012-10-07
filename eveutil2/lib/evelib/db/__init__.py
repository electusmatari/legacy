# EVE DB Accessors. Uses twf.

import twf.db as db
import twf.futil as futil

class DBRow(futil.Row):
    """
    A DBRow is a row in a database.
    """
    def __new__(cls, c, row):
        obj = super(DBRow, cls).__new__(cls, row._header, row)
        obj._c = c
        return obj

    @classmethod
    def _table(cls):
        if not hasattr(cls, '__table'):
            cls.__table = "ccp." + cls.__name__.lower()
        return cls.__table

    @classmethod
    def get(cls, c, col, val):
        c.execute("SELECT * FROM %s WHERE %s = %%s" %
                  (cls._table(), col),
                  (val,))
        if c.rowcount == 0:
            raise RowDoesNotExistError("Table %s, column %s = %r "
                                       "does not exist" %
                                       (cls._table(), col, val))
        else:
            return cls(c, c.fetchone())

    @classmethod
    def getlist(cls, c, col, val):
        c.execute("SELECT * FROM %s WHERE %s = %%s" %
                  (cls._table(), col),
                  (val,))
        return [cls(c, row) for row in c.fetchall()]

class cached(object):
    def __init__(self, func):
        self._func = func
        self.__name__ = func.__name__
        self.__doc__ = func.__doc__
 
    def __get__(self, obj, obj_class):
        if obj is None:
            return obj
        obj.__dict__[self.__name__] = self._func(obj)
        return obj.__dict__[self.__name__]

class RowDoesNotExistError(Exception):
    pass

class invTypes(DBRow):
    def __cmp__(self, other):
        if hasattr(other, 'typeid'):
            return self.typeid == other.typeid
        else:
            return False

    @cached
    def blueprint(self):
        try:
            return invBlueprintTypes.get(self._c, 'producttypeid', self.typeid)
        except RowDoesNotExistError:
            return None

    @cached
    def group(self):
        return invGroups.get(self._c, 'groupid', self.groupid)

    @cached
    def metagroup(self):
        self._c.execute("SELECT mg.metagroupname "
                        "FROM ccp.invmetatypes mt "
                        "     INNER JOIN ccp.invmetagroups mg "
                        "       ON mt.metagroupid = mg.metagroupid "
                        "WHERE mt.typeid = %s",
                        (self.typeid,))
        if self._c.rowcount == 0:
            return None
        else:
            return self._c.fetchone()[0]

    @cached
    def parenttype(self):
        self._c.execute("SELECT t.* "
                        "FROM ccp.invtypes t "
                        "     INNER JOIN ccp.invmetatypes mt "
                        "       ON mt.parenttypeid = t.typeid "
                        "WHERE mt.typeid = %s",
                        (self.typeid,))
        if self._c.rowcount == 0:
            return None
        else:
            return invTypes(self._c, self._c.fetchone())

    def attribute(self, name):
        self._c.execute("SELECT COALESCE(ta.valuefloat, ta.valueint) "
                        "FROM ccp.dgmtypeattributes ta "
                        "     INNER JOIN ccp.dgmattributetypes at "
                        "       ON ta.attributeid = at.attributeid "
                        "WHERE at.attributename = %s "
                        "  AND ta.typeid = %s",
                        (name, self.typeid))
        if self._c.rowcount == 0:
            return None
        else:
            return self._c.fetchone()[0]

    @cached
    def materials(self):
        self._c.execute("SELECT tm.quantity, rt.* "
                        "FROM ccp.invtypematerials tm "
                        "     INNER JOIN ccp.invtypes rt "
                        "       ON tm.materialtypeid = rt.typeid "
                        "WHERE tm.typeid = %s",
                        (self.typeid,))
        return [(invTypes(self._c, row), row[0])
                for row in self._c.fetchall()]

    @cached
    def marketgroup(self):
        return invMarketGroups.get(self._c, 'marketgroupid',
                                   self.marketgroupid)

    @cached
    def marketgroups(self):
        groups = []
        if not self.marketgroupid:
            return groups
        mg = self.marketgroup
        groups.append(mg)
        while mg.parentgroupid:
            mg = mg.parentgroup
            groups.append(mg)
        return groups

    def typerequirements(self, activity):
        self._c.execute("SELECT tr.requiredtypeid, "
                        "       tr.quantity, "
                        "       tr.damageperjob, "
                        "       tr.recycle "
                        "FROM ccp.ramtyperequirements tr "
                        "     INNER JOIN ccp.ramactivities act "
                        "       ON tr.activityid = act.activityid "
                        "WHERE tr.typeid = %s "
                        "  AND act.activityname = %s",
                        (self.typeid, activity))
        return [(invTypes.get(self._c, 'typeid', reqtypeid),
                 qty, dpj, recycle)
                for (reqtypeid, qty, dpj, recycle) in self._c.fetchall()]


class invGroups(DBRow):
    @cached
    def category(self):
        return invCategories.get(self._c, 'categoryid', self.categoryid)

class invCategories(DBRow):
    pass

class invMarketGroups(DBRow):
    @cached
    def parentgroup(self):
        return invMarketGroups.get(self._c, 'marketgroupid',
                                   self.parentgroupid)

class invBlueprintTypes(DBRow):
    @cached
    def blueprinttype(self):
        return invTypes.get(self._c, 'typeid', self.blueprinttypeid)

    @cached
    def producttype(self):
        return invTypes.get(self._c, 'typeid', self.producttypeid)

    def typerequirements(self, activity):
        self._c.execute("SELECT tr.requiredtypeid, "
                        "       tr.quantity, "
                        "       tr.damageperjob, "
                        "       tr.recycle "
                        "FROM ccp.ramtyperequirements tr "
                        "     INNER JOIN ccp.ramactivities act "
                        "       ON tr.activityid = act.activityid "
                        "WHERE tr.typeid = %s "
                        "  AND act.activityname = %s",
                        (self.blueprinttypeid, activity))
        return [(invTypes.get(self._c, 'typeid', reqtypeid),
                 qty, dpj, recycle)
                for (reqtypeid, qty, dpj, recycle) in self._c.fetchall()]

    @cached
    def inventionblueprints(self):
        """
        All blueprints we can invent from this one.

        Producttypeid is the invmetatypes.parenttypeid of the 'Tech
        II' invmetagroup. All other typeids in that group can be
        invented.
        """
        self._c.execute("SELECT sbt.* "
                        "FROM ccp.invmetatypes mt "
                        "     INNER JOIN ccp.invblueprinttypes sbt "
                        "       ON mt.typeid = sbt.producttypeid "
                        "     INNER JOIN ccp.invmetagroups mg "
                        "       ON mt.metagroupid = mg.metagroupid "
                        "WHERE mt.parenttypeid = %s "
                        "  AND mg.metagroupname = 'Tech II'",
                        (self.producttypeid,))
        return [invBlueprintTypes(self._c, row) for row in self._c.fetchall()]
