# Industry-related DB access

import collections

import twf.db as db
from evelib.db import *

def manufacturing(product, bp):
    c = db.cursor('dbeve')
    # First, take the base materials
    base = Basket()
    for (invtype, qty) in product.materials:
        base[invtype] = qty
    # Now, add additional materials. We do this before we add
    # efficiency, as this might change the base materials.
    more = Basket()
    typereqs = product.blueprint.typerequirements('Manufacturing')
    for (reqtype, qty, dpj, recycle) in typereqs:
        if dpj < 0.00001:
            continue
        if recycle > 0:
            for (invtype, reqqty) in reqtype.materials:
                if reqqty > base[invtype]:
                    del base[invtype]
                else:
                    base[invtype] = base[invtype] - reqqty
        if dpj > 0.99999:
            more[reqtype] = qty
        else:
            more[reqtype] = qty * dpj
    # Now we add the ME level to the base values
    bwf = product.blueprint.wastefactor
    if bp.me >= 0:
        wf = bwf * 0.01 * (1.0 / (bp.me + 1))
    else:
        wf = bwf * 0.01 * (1 - bp.me)
    for (key, val) in base.items():
        base[key] += int(round(val * wf))
    return base + more

def cost(invtype, iconf):
    price = iconf.index(invtype)
    if price is not None:
        return price        
    tl = int(invtype.attribute("techLevel") or 1.0)
    bp = iconf.get_blueprint(invtype)
    materials = manufacturing(invtype, bp)
    for type, qty in bp.extra_items:
        materials[type] += qty
    price = materialcost(materials, iconf) / invtype.portionsize
    return price * bp.safetymargin

def materialcost(materials, iconf):
    total = 0
    for invtype, qty in materials.items():
        total += cost(invtype, iconf) * qty
    return total

class Blueprint(object):
    def __init__(self, product=None, me=0, safetymargin=1.0):
        self.product = product
        self.me = me
        self.safetymargin = safetymargin

    @property
    def extra_items(self):
        return []

class InventedBlueprint(Blueprint):
    def __init__(self, product, safetymargin=1.0, decryptor=None):
        if decryptor is None:
            self.decryptor = NoDecryptor()
        else:
            self.decryptor = decryptor
        self.product = product
        (chance, runs) = self.chance_and_runs()
        self.invention_chance = chance * decryptor.chance_modifier
        self.invention_runs = runs + decryptor.run_modifier
        me = -4 + decryptor.me_modifier
        super(InventedBlueprint, self).__init__(product, me, safetymargin)

    def chance_and_runs(self):
        cat = self.product.group.category.categoryname
        chance = None
        runs = None
        if cat in ['Module', 'Charge', 'Drone']:
            (chance, runs) = (0.4, 10)
        elif cat in ['Deployable']:
            (chance, runs) = (0.4, 5)
        elif cat in ['Ship']:
            group = self.product.parenttype.group.groupname
            if self.product.typename == 'Hulk':
                (chance, runs) = (0.2, 1)
            elif self.product.typename == 'Mackinaw':
                (chance, runs) = (0.25, 1)
            elif self.product.typename == 'Skiff':
                (chance, runs) = (0.3, 1)
            elif group in ['Frigate', 'Destroyer', 'Freighter']:
                (chance, runs) = (0.3, 1)
            elif group in ['Cruiser', 'Industrial']:
                (chance, runs) = (0.25, 1)
            elif group in ['Battlecruiser', 'Battleship']:
                (chance, runs) = (0.2, 1)
        if chance is None:
            raise RuntimeError("No invention for category %s (%s)" %
                               (cat, self.product.typename))
        return (chance, runs)

    @property
    def extra_items(self):
        c = db.cursor('dbeve')
        t2product = self.product
        t1bp = t2product.parenttype.blueprint
        result = Basket()
        chance = self.invention_chance
        runs = self.invention_runs
        for (reqtype, qty, dpj, recycle) in t1bp.typerequirements("Invention"):
            if dpj < 0.00001:
                continue
            # Evil hack, these should have dpj = 0, but don't
            if reqtype.group.groupname == 'Data Interfaces':
                continue
            result[reqtype] = qty * (1.0/chance) * (1.0/runs)
        if self.decryptor.invtype is not None:
            result[self.decryptor.invtype] = (1.0/chance) * (1.0/runs)
        return result.items()

class Decryptor(object):
    def __init__(self, invtype, me_modifier, chance_modifier, run_modifier):
        self.invtype = invtype
        self.me_modifier = me_modifier
        self.chance_modifier = chance_modifier
        self.run_modifier = run_modifier

class NoDecryptor(Decryptor):
    def __init__(self):
        super(NoDecryptor, self).__init__(invtype=None,
                                          me_modifier=+0,
                                          chance_modifier=1.0,
                                          run_modifier=+0)

# Decryptor1 =  {'me': -2, 'chance': 0.6, 'runs': +9}
# Decryptor2 =  {'me': +1, 'chance': 1.0, 'runs': +2}
# Decryptor3 =  {'me': +3, 'chance': 1.1, 'runs': +0}
# Decryptor4 =  {'me': +2, 'chance': 1.2, 'runs': +1}
# Decryptor5 =  {'me': -1, 'chance': 1.8, 'runs': +4}

### T3
RELICS = {
    'Strategic Cruiser': [('Intact Hull Section', 0.4, 10),
                          ('Malfunctioning Hull Section', 0.3, 10),
                          ('Wrecked Hull Section', 0.2, 3)],
    'Offensive Systems': [('Intact Weapon Subroutines', 0.4, 20),
                          ('Malfunctioning Weapon Subroutines', 0.3, 10),
                          ('Wrecked Weapon Subroutines', 0.2, 3)],
    'Defensive Systems': [('Intact Armor Nanobot', 0.4, 20),
                          ('Malfunctioning Armor Nanobot', 0.3, 10),
                          ('Wrecked Armor Nanobot', 0.2, 3)],
    'Electronic Systems': [('Intact Electromechanical Component', 0.4, 20),
                           ('Malfunctioning Electromechanical Component', 0.3, 10),
                           ('Wrecked Electromechanical Component', 0.2, 3)],
    'Engineering Systems': [('Intact Power Cores', 0.4, 20),
                            ('Malfunctioning Power Cores', 0.3, 10),
                            ('Wrecked Power Cores', 0.2, 3)],
    'Propulsion Systems': [('Intact Thruster Sections', 0.4, 20),
                           ('Malfunctioning Thruster Sections', 0.3, 10),
                           ('Wrecked Thruster Sections', 0.2, 3)]
    }

DECRYPTORS = {
    1: 'Caldari Hybrid Tech Decryptor',
    2: 'Minmatar Hybrid Tech Decryptor',
    4: 'Amarr Hybrid Tech Decryptor',
    8: 'Gallente Hybrid Tech Decryptor'
    }

class ReverseEngineeredBlueprint(Blueprint):
    def __init__(self, product, safetymargin=1.0):
        super(ReverseEngineeredBlueprint, self).__init__(product,
                                                         0,
                                                         safetymargin)

    @property
    def extra_items(self):
        c = db.cursor('dbeve')
        t3product = self.product
        relics = [(invTypes.get(c, 'typename', relic),
                   Basket(), 
                   chance * (1 + (0.01 * 4)) * (1 + (0.1 * (4 + 4))),
                   runs)
                  for (relic, chance, runs)
                  in RELICS[t3product.group.groupname]]
        for (relic, basket, chance, runs) in relics:
            # Artifact
            basket[relic] = 1 * (1.0/chance) * (1.0/runs)
            # Decryptors
            decryptor = invTypes.get(c, 'typename', 
                                     DECRYPTORS[t3product.raceid])
            basket[decryptor] = 1 * (1.0/chance) * (1.0/runs)
            # Rest
            for (reqtype, qty, dpj,
                 recycle) in relic.typerequirements("Reverse Engineering"):
                if dpj < 0.00001:
                    continue
                basket[reqtype] = qty * (1.0/chance) * (1.0/runs)
        (intact, malfunctioning, wrecked) = relics
        result = (wrecked[1] * 4 + malfunctioning[1]) * 0.2
        return result.items()


class Basket(object):
    def __init__(self):
        self.quantities = {}
        self.invtypes = {}

    def __repr__(self):
        return "<Basket with %s>" % (", ".join(["%sx %r" % (value, key)
                                                for key, value
                                                in self.quantities.items()]))

    def __setitem__(self, invtype, value):
        self.quantities[invtype.typename] = value
        self.invtypes[invtype.typename] = invtype

    def __getitem__(self, invtype):
        self.quantities.setdefault(invtype.typename, 0)
        self.invtypes.setdefault(invtype.typename, invtype)
        return self.quantities[invtype.typename]

    def __delitem__(self, invtype):
        del self.quantities[invtype.typename]
        del self.invtypes[invtype.typename]

    def items(self):
        return [(self.invtypes[k], v) for (k, v) in self.quantities.items()]

    def __add__(self, other):
        d = Basket()
        for (key, value) in self.items():
            d[key] = value
        for (key, value) in other.items():
            d[key] += value
        return d

    def __sub__(self, other):
        d = Basket()
        for (key, value) in self.items():
            d[key] = value
        for (key, value) in other.items():
            d[key] -= value
        return d

    def __mul__(self, multiplier):
        d = Basket()
        for (key, value) in self.items():
            d[key] = value * multiplier
        return d
