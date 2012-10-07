import sys
sys.path.append("/home/forcer/Projects/eveutil/dev/bin/")

from lib import evedb, util

import datetime

db = evedb.connect()

MINERALS = ['Tritanium', 'Pyerite', 'Mexallon', 'Isogen',
            'Nocxium', 'Zydrine', 'Megacyte']

COMP = ["800mm Repeating Artillery I",
        # "1400mm Howitzer Artillery I",
        # "Warp Disruption Field Generator I",
        # "1200mm Artillery Cannon I",
        # "Purgatory Citadel Torpedo",
        "Doom Citadel Torpedo",
        # "100MN MicroWarpdrive I",
        # "Large EMP Smartbomb I",
        # "EMP XL",
        # "Doom Citadel Torpedo",
        # "Thor Citadel Torpedo",
        # "Phased Plasma XL"
        ]

_modvol = {}
def modvol(module):
    if module not in _modvol:
        c = db.cursor()
        c.execute("SELECT volume * portionsize FROM invtypes "
                  "WHERE typename = %s",
                  (module,))
        _modvol[module] = c.fetchone()[0]
    return _modvol[module]

def compress(basket):
    agenda = [Shipment([(mod, mineralneed(mod)) for mod in COMP],
                       basket)]
    minvol = agenda[0].volume
    minshipment = agenda[0]
    started = datetime.datetime.now()
    lasttime = None
    loop = 0L
    while len(agenda) > 0:
        if loop % 10000 == 0:
            runtime = (datetime.datetime.now() - started).seconds
            if runtime != lasttime and runtime % 15 == 0:
                lasttime = runtime
                print
                print "** %s" % len(agenda)
                print minshipment
                print minshipment.cargo
                print minshipment.minerals
        loop += 1
        now = agenda[0]
        agenda = agenda[1:]
        agenda = now.compress() + agenda
        # agenda.sort(lambda a, b: cmp(a.volume, b.volume))
        if now.volume < minvol:
            minvol = now.volume
            minshipment = now
    return minshipment

class Shipment(object):
    def __init__(self, comps, minerals, cargo={}, next=0, maxvolume=None):
        self.comps = comps
        self.minerals = minerals
        self.cargo = cargo.copy()
        self.computevolume()
        if maxvolume is None:
            self.maxvolume = self.volume
        else:
            self.maxvolume = maxvolume
        self.next = next

    def __repr__(self):
        return("<Shipment there: %s m3 / back: %s m3>" %
               (self.volume, self.backvolume))

    def addcargo(self, typename, amount):
        self.cargo.setdefault(typename, 0)
        self.cargo[typename] += amount
        self.computevolume()

    def computevolume(self):
        self.volume = 0
        self.backvolume = 0
        for (typename, qty) in self.cargo.items():
            self.volume += qty * modvol(typename)
        self.volume += self.minerals.posvolume()
        self.backvolume = self.minerals.negvolume()

    def compress(self):
        if self.next >= len(self.comps):
            return []
        (name, basket) = self.comps[self.next]
        maxnum = int(self.minerals / basket)
        if maxnum == 0:
            return []
        amounts = range(0, maxnum, stepsize(maxnum)) + [maxnum]
        amounts.reverse()
        result = []
        for i in amounts:
            newminerals = self.minerals - basket * i
            if newminerals.allnegative():
                continue
            if (newminerals.posvolume() > self.maxvolume
                or newminerals.negvolume() > self.maxvolume):
                continue
            newshipment = Shipment(self.comps, newminerals,
                                   cargo=self.cargo,
                                   next=self.next + 1,
                                   maxvolume=self.maxvolume)
            if i > 0:
                newshipment.addcargo(name, i)
            if newshipment.volume < newshipment.backvolume:
                continue
            result.append(newshipment)
        return result

def stepsize(maxnum):
    return 1 # max(1, int(maxnum/80))

class MineralBasket(object):
    def __init__(self, initial={}):
        self.minerals = dict((m, initial.get(m, 0))
                             for m in MINERALS)

    def volume(self):
        return sum(self.minerals.values()) * 0.01

    def posvolume(self):
        return sum(x for x in self.minerals.values() if x > 0) * 0.01

    def negvolume(self):
        return sum(-1*x for x in self.minerals.values() if x < 0) * 0.01

    def absvolume(self):
        return sum(abs(x) for x in self.minerals.values()) * 0.01

    def negative(self):
        for val in self.minerals.values():
            if val < 0:
                return True
        return False

    def allnegative(self):
        for val in self.minerals.values():
            if val >= 0:
                return False
        return True

    def __repr__(self):
        return ("<MineralBasket %s>" %
                ", ".join(["%sx %s" % (util.humane(self[m]), m)
                           for m in MINERALS]))

    def __getitem__(self, name):
        return self.minerals[name]

    def __setitem__(self, name, value):
        self.minerals[name] = value

    def __gt__(self, other):
        for m in MINERALS:
            if self.get(m, 0) < other.get(m, 0):
                return False
        return True

    def __ge__(self, other):
        for m in MINERALS:
            if self.get(m, 0) <= other.get(m, 0):
                return False
        return True

    def __lt__(self, other):
        for m in MINERALS:
            if self.get(m, 0) > other.get(m, 0):
                return False
        return True

    def __le__(self, other):
        for m in MINERALS:
            if self.get(m, 0) >= other.get(m, 0):
                return False
        return True

    def __div__(self, other):
        n = 0
        for m in MINERALS:
            if self[m] == 0 or other[m] == 0:
                continue
            n = max(n, self[m] / float(other[m]))
        return n

    def __mul__(self, n):
        result = MineralBasket()
        for m in MINERALS:
            result[m] = self[m] * n
        return result

    def __add__(self, other):
        result = MineralBasket()
        for m in MINERALS:
            result[m] = self[m] + other[m]
        return result

    def __sub__(self, other):
        result = MineralBasket()
        for m in MINERALS:
            result[m] = self[m] - other[m]
        return result

def mineralneed(typename):
    mins = MineralBasket()
    mats = materials(typename)
    while len(mats) > 0:
        (mat, qty) = mats[0]
        mats = mats[1:]
        if mat in MINERALS:
            mins[mat] += qty
        else:
            mats.extend([(smat, sqty * qty)
                         for (smat, sqty)
                         in materials(mat)])
    return mins

def materials(typename):
    c = db.cursor()
    c.execute("SELECT mt.typename, tm.quantity "
              "FROM invtypematerials tm "
              "     INNER JOIN invtypes t "
              "       ON tm.typeid = t.typeid "
              "     INNER JOIN invtypes mt "
              "       ON tm.materialtypeid = mt.typeid "
              "WHERE t.typename = %s",
              (typename,))
    if c.rowcount == 0:
        raise RuntimeException("No materials for type %s" % (typename,))
    return c.fetchall()
              


# def compress(ship):
#     total = mineralneed(ship)
#     comps = []
#     for c in COMP:
#         compneed = mineralneed(c)
#         take = int(total / compneed)
#         comps.append(generate(c, compneed, take))
#     minvol = 500000000000
#     result = None
#     for comb in combinations(comps):
#         types = []
#         backtypes = []
#         shipvolume = 0
#         backvolume = 0
#         remain = total
#         for (typename, basket, qty) in comb:
#             if qty == 0:
#                 continue
#             remain -= basket * qty
#             types.append((qty, typename))
#             shipvolume += modvol(typename) * qty
#         for (m, qty) in remain.minerals.items():
#             if qty > 0:
#                 shipvolume += qty * 0.01
#                 types.append((qty, m))
#             else:
#                 backvolume += abs(qty) * 0.01
#                 backtypes.append((abs(qty), m))
#         if shipvolume > 0 and shipvolume < minvol:
#             minvol = shipvolume
#             result = (shipvolume, types, backvolume, backtypes)
#     return result
# 
# def combinations(t):
#     """
#     List of lists. Return a list of lists, each element one of the
#     elements of that tuple place.
#     """
#     if len(t) == 1:
#         return [[x] for x in t[0]]
#     else:
#         result = []
#         for x in t[0]:
#             for tail in combinations(t[1:]):
#                 result.append([x] + tail)
#         return result
# 
# def generate(comp, need, take):
#     step = int(take / 5)
#     amounts = range(0, take, step) + [take]
#     return [(comp, need, amount) for amount in amounts]


if __name__ == '__main__':
    # s = compress(mineralneed("Nidhoggur") + mineralneed("Thanatos")
    #              + mineralneed("Naglfar") + mineralneed("Moros"))
    s = compress(mineralneed("Thanatos"))
    print
    print "** DONE **"
    print s
    print s.cargo
    print s.minerals
