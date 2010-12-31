import datetime

from django.db import models
from django.contrib.auth.models import User

from emtools.ccpeve import ccpdb

class IndexHistory(models.Model):
    timestamp = models.DateField()
    typeid = models.BigIntegerField()
    republic = models.FloatField()
    republicvolume = models.BigIntegerField()
    republicchange = models.FloatField(null=True)
    heimatar = models.FloatField()
    heimatarvolume = models.BigIntegerField()
    heimatarchange = models.FloatField(null=True)
    heimatarage = models.IntegerField(null=True)
    metropolis = models.FloatField()
    metropolisvolume = models.BigIntegerField()
    metropolischange = models.FloatField(null=True)
    metropolisage = models.IntegerField(null=True)
    moldenheath = models.FloatField()
    moldenheathvolume = models.BigIntegerField()
    moldenheathchange = models.FloatField(null=True)
    moldenheathage = models.IntegerField(null=True)
    jita = models.FloatField()
    jitavolume = models.BigIntegerField()
    jitachange = models.FloatField(null=True)
    jitaage = models.IntegerField(null=True)

    @property
    def typename(self):
        return ccpdb.get_typename(self.typeid)

    @property
    def heimatarclass(self):
        return ageclass(self.heimatarage)
            
    @property
    def metropolisclass(self):
        return ageclass(self.metropolisage)
            
    @property
    def moldenheathclass(self):
        return ageclass(self.moldenheathage)
            
    @property
    def jitaclass(self):
        return ageclass(self.jitaage)
            
def ageclass(age):
    if age is None:
        return 'never'
    elif age > 7:
        return 'veryold'
    elif age > 3:
        return 'old'
    else:
        return 'new'

class Index(models.Model):
    latest = models.OneToOneField(IndexHistory, primary_key=True)

class Upload(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User)
    regionid = models.BigIntegerField()
    typeid = models.BigIntegerField()
    calltimestamp = models.DateTimeField()

    @property
    def region(self):
        return ccpdb.get_regionname(self.regionid)

    @property
    def typename(self):
        return ccpdb.get_typename(self.typeid)

    class Meta:
        ordering = ["-timestamp"]
