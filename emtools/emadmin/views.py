import datetime

from django.contrib.auth.models import User
from django.views.generic.list_detail import object_list
from django.views.generic.simple import direct_to_template

from emtools.emauth.decorators import require_admin
from emtools.emadmin.models import LogRecord, Schedule

from emtools import utils

OLD_DAYS = 7

@require_admin
def view_log(request):
    return object_list(request, LogRecord.objects.all(),
                       paginate_by=23,
                       template_name='emadmin/log.html',
                       extra_context={'tab': 'log'},
                       template_object_name='log')

@require_admin
def view_status(request):
    return direct_to_template(request, 'emadmin/status.html',
                              extra_context={'tab': 'status',
                                             'schedule_list':
                                                 Schedule.objects.all()})

IGNORED_GROUPS = ['Registered', 'Awaiting Activation', 'Banned']

@require_admin
def view_groups(request):
    db = utils.connect('emforum')
    c = db.cursor()
    c.execute("SELECT gid, title FROM mybb_usergroups")
    gid2name = dict(c.fetchall())
    c.execute("SELECT uid, username, lastactive, usergroup, additionalgroups "
              "FROM mybb_users")
    group_users = {}
    now = datetime.datetime.utcnow()
    for (mybb_uid, mybb_username, lastactive,
         usergroup, additionalgroups) in c.fetchall():
        try:
            user = User.objects.get(profile__mybb_uid=mybb_uid)
        except User.DoesNotExist:
            user = None
        lastactive = datetime.datetime.utcfromtimestamp(lastactive)
        delta = now - lastactive
        gids = [usergroup] + [int(gid) for gid in additionalgroups.split(",")
                              if gid != '']
        for gid in gids:
            group = gid2name.get(gid, "<Group %i>" % gid)
            if group in IGNORED_GROUPS:
                continue
            group_users.setdefault(group, [])
            group_users[group].append({'name': mybb_username,
                                       'user': user,
                                       'lastactive': lastactive,
                                       'days': delta.days,
                                       'cssclass': ('veryold'
                                                    if delta.days > OLD_DAYS
                                                    else '')})
    for users in group_users.values():
        users.sort(lambda a, b: cmp(a['name'].lower(), b['name'].lower()))
    groups = [(name, len(users), users)
              for (name, users) in group_users.items()]
    groups.sort(lambda a, b: cmp(a[0].lower(), b[0].lower()))
    return direct_to_template(request, 'emadmin/groups.html',
                              extra_context={'tab': 'groups',
                                             'group_list': groups})
