import datetime

from emtools.ccpeve import eveapi
from django.db import models

class APIKey(models.Model):
    name = models.CharField(max_length=255)
    userid = models.CharField(max_length=32)
    apikey = models.CharField(max_length=128)
    characterid = models.CharField(max_length=32)
    active = models.BooleanField()
    message = models.TextField(max_length=255, blank=True)
    last_attempt = models.DateTimeField()

    def __str__(self):
        return "API Key %s" % self.name

    def root(self):
        return apiroot(userID=self.userid, apiKey=self.apikey)

    def char(self):
        return apichar(userID=self.userid, apiKey=self.apikey,
                       characterID=self.characterid)

    def corp(self):
        return apicorp(userID=self.userid, apiKey=self.apikey,
                       characterID=self.characterid)

class Cache(models.Model):
    cacheduntil = models.DateTimeField()
    host = models.CharField(max_length=255)
    path = models.CharField(max_length=255)
    params = models.TextField()
    doc = models.TextField()

def apiroot(userID=None, apiKey=None):
    api = eveapi.EVEAPIConnection(cacheHandler=DBCache())
    if userID is not None and apiKey is not None:
        api = api.auth(userID=userID, apiKey=apiKey)
    return api

def apichar(userID, apiKey, characterID):
    api = apiroot(userID, apiKey)
    return api.character(characterID=characterID)

def apicorp(userID, apiKey, characterID):
    api = apiroot(userID, apiKey)
    return api.corporation(characterID=characterID)

class DBCache(object):
    def retrieve(self, host, path, params):
        try:
            cached = Cache.objects.exclude(
                cacheduntil__lt=datetime.datetime.utcnow()
                ).get(host=host, path=path, params=repr(params))
        except Cache.DoesNotExist:
            return None
        return cached.doc.encode("utf-8")

    def store(self, host, path, params, doc, obj):
        Cache.objects.filter(
            host=host, path=path, params=repr(params)
            ).delete()
        cacheduntil = datetime.datetime.utcfromtimestamp(obj.cachedUntil)
        cached = Cache(host=host, path=path, params=repr(params),
                       doc=doc, cacheduntil=cacheduntil)
        cached.save()

class MarketHistory(models.Model):
    regionid = models.BigIntegerField()
    typeid = models.BigIntegerField()
    historydate = models.DateField()
    lowprice = models.FloatField()
    highprice = models.FloatField()
    avgprice = models.FloatField()
    volume = models.BigIntegerField()
    orders = models.IntegerField()
