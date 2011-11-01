import datetime

from django.views.generic.simple import direct_to_template
from emtools.ccpeve.models import apiroot
import emtools.ccpeve.igb as igb

import sys
sys.path.append("/home/forcer/Projects/gradient")

from gradient.uploader.models import FacWarSystem
from emtools.intel.models import Pilot, Corporation, Faction

def view_map(request):
    lu = FacWarSystem.objects.all()[0].cachetimestamp
    minmatar = FacWarSystem.objects.filter(
        occupyingfactionname='Minmatar Republic',
        victorypoints__gt=0).order_by('-victorypoints')
    amarr = FacWarSystem.objects.filter(
        occupyingfactionname='Amarr Empire',
        victorypoints__gt=0).order_by('-victorypoints')
    gallente = FacWarSystem.objects.filter(
        occupyingfactionname='Gallente Federation',
        victorypoints__gt=0).order_by('-victorypoints')
    caldari = FacWarSystem.objects.filter(
        occupyingfactionname='Caldari State',
        victorypoints__gt=0).order_by('-victorypoints')
    return direct_to_template(request, 'fw/map.html',
                              extra_context={
            'tab': 'map',
            'lastupdated': lu,
            'map': [('Minmatar Republic', '/media/img/icons/minmatar.png',
                     minmatar),
                    ('Amarr Empire', '/media/img/icons/amarr.png', amarr),
                    ('Gallente Federation', '/media/img/icons/gallente.png',
                     gallente),
                    ('Caldari State', '/media/img/icons/caldari.png',
                     caldari),
                    ]
            })

def corp_image(corpid):
    try:
        corp = Corporation.objects.select_related(
            depth=1).get(corporationid=corpid)
    except Corporation.DoesNotExist:
        return None
    return faction_image(corp.faction)

def pilot_image(charid):
    try:
        pilot = Pilot.objects.select_related(
            depth=2).get(characterid=charid)
    except Corporation.DoesNotExist:
        return None
    return faction_image(pilot.corporation.faction)

def faction_image(faction):
    if faction is None:
        return None
    elif faction.name == 'Minmatar Republic':
        return '/media/img/icons/minmatar16.png'
    elif faction.name == 'Amarr Empire':
        return '/media/img/icons/amarr16.png'
    elif faction.name == 'Gallente Federation':
        return '/media/img/icons/gallente16.png'
    elif faction.name == 'Caldari State':
        return '/media/img/icons/caldari16.png'
    else:
        return None

def view_topstats(request):
    api = apiroot()
    fwts = api.eve.FacWarTopStats()

    vplastweek = Bag(characters=[],
                     corporations=[],
                     factions=[])
    for rank, entry in enumerate(fwts.characters.VictoryPointsLastWeek):
        vplastweek.characters.append(Bag(rank=rank + 1,
                                         id=entry.characterID,
                                         name=entry.characterName,
                                         points=entry.victoryPoints,
                                         igb=igb.ShowInfoCharacter(entry.characterID),
                                         faction=pilot_image(entry.characterID)))
    for rank, entry in enumerate(fwts.corporations.VictoryPointsLastWeek):
        vplastweek.corporations.append(Bag(rank=rank + 1,
                                           id=entry.corporationID,
                                           name=entry.corporationName,
                                           points=entry.victoryPoints,
                                           igb=igb.ShowInfoCorp(entry.corporationID),
                                           faction=corp_image(entry.corporationID)))
    for rank, entry in enumerate(fwts.factions.VictoryPointsLastWeek):
        vplastweek.factions.append(Bag(rank=rank + 1,
                                       id=entry.factionID,
                                       name=entry.factionName,
                                       points=entry.victoryPoints,
                                       igb=""))
    return direct_to_template(request, 'fw/topstats.html',
                              extra_context={'tab': 'topstats',
                                             'vplastweek': vplastweek,
                                             'cacheduntil': datetime.datetime.utcfromtimestamp(fwts._meta.cachedUntil)})

class Bag(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
