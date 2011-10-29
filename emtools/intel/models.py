# CREATE UNIQUE INDEX intel_entity_name_key
#   ON intel_entity(entitytype, LOWER(name));
# ALTER TABLE intel_kill DROP CONSTRAINT intel_kill_system_id_fkey;

import base64
import datetime
import hashlib
import pickle

from django.contrib.auth.models import User
from django.db import models, IntegrityError, transaction, connection
from django.utils.safestring import mark_safe
from django.utils.html import escape

from emtools.ccpeve import igb
from emtools.ccpeve.models import apiroot, SolarSystem

##################################################################
# Factions

class Faction(models.Model):
    name = models.CharField(max_length=128)
    factionid = models.BigIntegerField(null=True)

##################################################################
# Alliances

class Alliance(models.Model):
    name = models.CharField(max_length=128)
    allianceid = models.BigIntegerField(null=True)
    ticker = models.CharField(max_length=12, null=True)
    members = models.IntegerField(null=True)
    standing = models.IntegerField(null=True)

    lastseen = models.DateTimeField(auto_now=True)
    lastkillinfo = models.DateTimeField(null=True)
    lastapi = models.DateTimeField(null=True)
    lastcache = models.DateTimeField(null=True)

    def fullname(self):
        if self.ticker:
            return "%s <%s>" % (self.name, self.ticker)
        else:
            return self.name

    def __unicode__(self):
        if self.standing is not None and self.standing != 0:
            if self.standing > 5:
                color = 'darkblue'
            elif self.standing > 0:
                color = 'blue'
            elif self.standing < -5:
                color = 'red'
            elif self.standing < 0:
                color = 'orange'
            tag = mark_safe('<img src="/media/img/icons/standings/%s.png" />' %
                            (color,))
        else:
            tag = mark_safe("")
                    
        link = mark_safe('<a href="/intel/alliance/%s" class="nobreak">%s</a>' %
                         (escape(self.name), escape(self.fullname())))
        showinfo = igb.ShowInfoAlliance(self.allianceid).__unicode__()
        return mark_safe('<span class="nobreak">') + link + tag + showinfo + mark_safe('</span>')

    class Meta:
        ordering = ["name"]

##################################################################
# Corporations

class Corporation(models.Model):
    name = models.CharField(max_length=128, blank=True)
    corporationid = models.BigIntegerField(null=True, default=None)
    faction = models.ForeignKey(Faction, null=True, default=None)
    alliance = models.ForeignKey(Alliance, null=True, default=None)
    ticker = models.CharField(max_length=12, null=True, default=None)
    members = models.IntegerField(null=True, default=None)
    standing = models.IntegerField(null=True, default=None)

    lastseen = models.DateTimeField(auto_now=True)
    lastkillinfo = models.DateTimeField(null=True, default=None)
    lastapi = models.DateTimeField(null=True, default=None)
    lastcache = models.DateTimeField(null=True, default=None)

    def fullname(self):
        if self.ticker:
            return "%s [%s]" % (self.name, self.ticker)
        else:
            return self.name

    def __unicode__(self):
        if self.standing is not None and self.standing != 0:
            if self.standing > 5:
                color = 'darkblue'
            elif self.standing > 0:
                color = 'blue'
            elif self.standing < -5:
                color = 'red'
            elif self.standing < 0:
                color = 'orange'
            tag = mark_safe('<img src="/media/img/icons/standings/%s.png" />' %
                            (color,))
        else:
            tag = mark_safe("")
        link = mark_safe('<a href="/intel/corp/%s" class="nobreak">%s</a>' %
                         (escape(self.name), escape(self.fullname())))
        showinfo = igb.ShowInfoCorp(self.corporationid).__unicode__()
        return mark_safe('<span class="nobreak">') + link + tag + showinfo + mark_safe('</span>')

    class Meta:
        ordering = ["name"]

    def update_from_killinfo(self, killtime, alliance, faction):
        # Corp comes from API or killinfo
        if ((self.lastapi is None or self.lastapi < killtime) and
            (self.lastkillinfo is None or self.lastkillinfo < killtime)):
            self.alliance = alliance
            self.faction = faction
            self.save()

##################################################################
# Pilots

class Pilot(models.Model):
    name = models.CharField(max_length=128, blank=True)
    characterid = models.BigIntegerField(null=True)
    corporation = models.ForeignKey(Corporation, null=True)
    alliance = models.ForeignKey(Alliance, null=True)
    security = models.FloatField(null=True)

    evewho = models.BooleanField(default=False)

    lastseen = models.DateTimeField(auto_now=True)
    lastkillinfo = models.DateTimeField(null=True)
    lastapi = models.DateTimeField(null=True)
    lastcache = models.DateTimeField(null=True)

    class Meta:
        ordering = ["name"]

    def __unicode__(self):
        link = mark_safe('<a href="/intel/pilot/%s" class="nobreak">%s</a>' %
                         (escape(self.name), escape(self.name)))
        showinfo = igb.ShowInfoCharacter(self.characterid).__unicode__()
        return mark_safe('<span class="nobreak">') + link + showinfo + mark_safe('</span>')

    def update_from_killinfo(self, killtime, corp, alliance):
        # Corp comes from API or killinfo
        if ((self.lastapi is None or self.lastapi < killtime) and
            (self.lastkillinfo is None or self.lastkillinfo < killtime)):
            self.corp = corp
            self.alliance = alliance
            self.save()

##################################################################
# Other models

class TrackedEntity(models.Model):
    corporation = models.ForeignKey(Corporation, null=True)
    alliance = models.ForeignKey(Alliance, null=True)

    def __unicode__(self):
        if self.corporation is not None:
            return self.corporation.name
        if self.alliance is not None:
            return self.alliance.name
        return "<Tracked Entity %i>" % self.id

class ChangeLog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    pilot = models.ForeignKey(Pilot)
    oldcorp = models.ForeignKey(Corporation, null=True,
                                related_name="changelog_old_set")
    newcorp = models.ForeignKey(Corporation, null=True,
                                related_name="changelog_new_set")
    oldalliance = models.ForeignKey(Alliance, null=True,
                                    related_name="changelog_old_set")
    newalliance = models.ForeignKey(Alliance, null=True,
                                    related_name="changelog_new_set")

    class Meta:
        ordering = ["-timestamp"]

class Trace(models.Model):
    submitted = models.DateTimeField(auto_now_add=True)
    timestamp = models.DateTimeField()
    pilot = models.ForeignKey(Pilot)
    corporation = models.ForeignKey(Corporation)
    alliance = models.ForeignKey(Alliance, null=True)
    system = models.CharField(max_length=128)
    systemid = models.IntegerField()
    # NULL means this was in space
    station = models.CharField(max_length=128, null=True)
    stationid = models.IntegerField(null=True)
    # NULL means this was from a kill mail, not from a locator agent
    agent = models.CharField(max_length=128, null=True)
    online = models.NullBooleanField()
    submitter = models.ForeignKey(User, null=True)

    class Meta:
        ordering = ["-timestamp"]

    def get_online_display(self):
        if self.online is None:
            return "Unknown"
        elif self.online is False:
            return "No"
        else:
            return "Yes"

    def get_system_display(self):
        showinfo = igb.ShowInfoSystem(self.systemid).__unicode__()
        return mark_safe(escape(self.system)) + showinfo

    def get_station_display(self):
        if self.station is None:
            return "In Space"
        else:
            showinfo = igb.ShowInfoStation(self.stationid).__unicode__()
            return mark_safe(escape(self.station)) + showinfo

##################################################################
# intel v2.0

class KillManager(models.Manager):
    def get_or_create_from_killinfo(self, ki, entity):
        unique = ("%s %s %s" %
                  (ki.killtime.strftime("%Y-%m-%dT%H:%M:%S"),
                   ki.solarsystemid,
                   ki.moonid or ki.victim.characterid))
        hash = hashlib.sha1(unique).hexdigest()
        try:
            return Kill.objects.get(hash=hash), False
        except Kill.DoesNotExist:
            pass
        obj = Kill()
        obj.timestamp = ki.killtime
        obj.system_id = ki.solarsystemid
        obj.hash = hash
        obj.pickle = base64.b64encode(pickle.dumps(ki, -1))
        sid = transaction.savepoint()
        try:
            obj.save()
            transaction.savepoint_commit(sid)
        except IntegrityError:
            transaction.savepoint_rollback(sid)
            return Kill.objects.get(hash=hash), False
        for p in [ki.victim] + ki.attackers:
            pilot = None
            corp = None
            alliance = None
            faction = None
            if p.charactername:
                pilot, created = entity.get_pilot(p.characterid,
                                                  p.charactername)
                obj.involvedpilots.add(pilot)
            if p.corporationname:
                corp, created = entity.get_corp(p.corporationid,
                                                p.corporationname)
                obj.involvedcorps.add(corp)
            if p.alliancename:
                alliance, created = entity.get_alliance(p.allianceid,
                                                        p.alliancename)
                obj.involvedalliances.add(alliance)
            if p.factionname:
                faction, created = entity.get_faction(p.factionid,
                                                      p.factionname)
                obj.involvedfactions.add(faction)
            if pilot is not None:
                pilot.update_from_killinfo(ki.killtime,
                                           corp=corp, alliance=alliance)
            if corp is not None:
                corp.update_from_killinfo(ki.killtime,
                                          alliance=alliance, faction=faction)
        return obj, True

class Kill(models.Model):
    objects = KillManager()

    timestamp = models.DateTimeField(db_index=True)
    system = models.ForeignKey(SolarSystem)
    hash = models.CharField(max_length=128, db_index=True, unique=True)
    pickle = models.TextField()
    original = models.TextField(null=True, blank=True, default=None)
    involvedpilots = models.ManyToManyField(Pilot)
    involvedcorps = models.ManyToManyField(Corporation)
    involvedalliances = models.ManyToManyField(Alliance)
    involvedfactions = models.ManyToManyField(Faction)

    def __unicode__(self):
        return self.hash

class Feed(models.Model):
    feedtype = models.CharField(max_length=32)
    url = models.CharField(max_length=255)
    state = models.TextField(null=True, default=None)
    failed_attempts = models.IntegerField(default=0)
    disabled = models.BooleanField(default=False)
    error = models.CharField(max_length=255, blank=True, default="")

    def __unicode__(self):
        return self.url
