from django.contrib.auth.models import User
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.html import escape

from emtools.ccpeve import igb

class Alliance(models.Model):
    name = models.CharField(max_length=128)
    allianceid = models.IntegerField()
    lastseen = models.DateTimeField(auto_now=True)
    ticker = models.CharField(max_length=12, null=True)
    members = models.IntegerField(null=True)
    standing = models.IntegerField(null=True)

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

class Corporation(models.Model):
    name = models.CharField(max_length=128)
    corporationid = models.IntegerField()
    alliance = models.ForeignKey(Alliance, null=True)
    lastseen = models.DateTimeField(auto_now=True)
    ticker = models.CharField(max_length=12, null=True)
    members = models.IntegerField(null=True)
    standing = models.IntegerField(null=True)

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

class Pilot(models.Model):
    name = models.CharField(max_length=128)
    characterid = models.IntegerField()
    corporation = models.ForeignKey(Corporation)
    alliance = models.ForeignKey(Alliance, null=True)
    lastseen = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __unicode__(self):
        link = mark_safe('<a href="/intel/pilot/%s" class="nobreak">%s</a>' %
                         (escape(self.name), escape(self.name)))
        showinfo = igb.ShowInfoCharacter(self.characterid).__unicode__()
        return mark_safe('<span class="nobreak">') + link + showinfo + mark_safe('</span>')

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
