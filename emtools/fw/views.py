import datetime

from django.views.generic.simple import direct_to_template
from emtools.ccpeve.models import apiroot
import emtools.ccpeve.igb as igb

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
                                         igb=igb.ShowInfoCharacter(entry.characterID)))
    for rank, entry in enumerate(fwts.corporations.VictoryPointsLastWeek):
        vplastweek.corporations.append(Bag(rank=rank + 1,
                                           id=entry.corporationID,
                                           name=entry.corporationName,
                                           points=entry.victoryPoints,
                                           igb=igb.ShowInfoCorp(entry.corporationID)))
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
