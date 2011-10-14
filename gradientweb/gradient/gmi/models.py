from django.db import models

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
            
class Index(models.Model):
    latest = models.OneToOneField(IndexHistory, primary_key=True)
