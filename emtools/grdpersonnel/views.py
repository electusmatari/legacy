import datetime

from django.views.generic.simple import direct_to_template
from emtools import utils
from emtools.ccpeve.models import apiroot, APIKey
from emtools.emauth.decorators import require_mybbgroup
import emtools.ccpeve.igb as igb

from collections import defaultdict

@require_mybbgroup(['Gradient Executive', 'Gradient Personnel Manager'])
def view_members(request):
    grd = APIKey.objects.get(name='Gradient').corp()
    ms = grd.MemberSecurity()
    mt = grd.MemberTracking()
    pilots = {}
    for member in ms.members:
        pilots.setdefault(member.name, defaultdict(lambda: ""))
        pilots[member.name]['id'] = member.characterID
        pilots[member.name]['titles'] = [title.titleName
                                         for title in member.titles]
        pilots[member.name]['roles'] = [role.roleName
                                        for role in member.roles]
    for member in mt.members:
        pilots.setdefault(member.name, defaultdict(lambda: ""))
        pilots[member.name]['id'] = member.characterID
        pilots[member.name]['start'] = datetime.datetime.utcfromtimestamp(member.startDateTime)
        pilots[member.name]['base'] = member.base
        pilots[member.name]['freeformtitle'] = member.title
        pilots[member.name]['logon'] = datetime.datetime.utcfromtimestamp(member.logonDateTime)
        pilots[member.name]['logoff'] = datetime.datetime.utcfromtimestamp(member.logoffDateTime)
        pilots[member.name]['location'] = member.location
        pilots[member.name]['ship'] = member.shipType

    personnel_threads = get_personnel_threads()

    prospect_count = 0
    norole_count = 0
    inactive_count = 0

    now = datetime.datetime.utcnow()
    for name, details in pilots.items():
        details['showinfo'] = igb.ShowInfoCharacter(details['id'])
        if 'roleDirector' in details['roles']:
            details['titles'].append('Director')
        if 'Prospect' not in details['titles'] and 'Employee' not in details['titles'] and 'Director' not in details['titles']:
            details['noroles'] = True
            norole_count += 1
        else:
            details['noroles'] = False
        start = details.get('start', datetime.datetime.utcnow())
        details['age'] = (now - start).days
        if 'Prospect' in details['titles']:
            details['prospect'] = True
            prospect_count += 1
            age = details['age']
            details['d30'] = age >= 30
            details['d60'] = age >= 60
            details['d120'] = age >= 120
        else:
            details['prospect'] = False
        details['lastactive'] = (now - details.get('logoff', now)).days
        if details['lastactive'] > 30 and 'on leave' not in details['freeformtitle'].lower():
            details['inactive'] = True
            inactive_count += 1
        else:
            details['inactive'] = False
        result = personnel_threads.get(name.lower())
        if result is None:
            details['tid'] = None
            prefix = None
        else:
            details['tid'], prefix = result
        if prefix == 20:
            details['canbepromoted'] = True
    pilots = pilots.items()
    pilots.sort(key=lambda a: a[0])
    return direct_to_template(request, 'grdpersonnel/members.html',
                              extra_context={
            'tab': 'members',
            'pilots': pilots,
            'cacheduntil': datetime.datetime.utcfromtimestamp(max(ms._meta.cachedUntil, mt._meta.cachedUntil)),
            'prospect_count': prospect_count,
            'norole_count': norole_count,
            'inactive_count': inactive_count})

def get_personnel_threads():
    db = utils.connect('emforum')
    c = db.cursor()
    c.execute("SELECT LOWER(subject), tid, prefix FROM mybb_threads "
              "WHERE fid IN (129, 130, 131)")
    return dict((subject, (tid, prefix))
                for (subject, tid, prefix) in c.fetchall())


class Bag(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
