import datetime

from emtools.ccpeve import eveapi
from django.db import models

from ccpmodels import *
from ccputils import InvItem

class APIKey(models.Model):
    name = models.CharField(max_length=255)
    userid = models.CharField(max_length=32)
    apikey = models.CharField(max_length=128)
    characterid = models.CharField(max_length=32)
    active = models.BooleanField()
    message = models.TextField(max_length=255, blank=True)
    last_attempt = models.DateTimeField()

    def __unicode__(self):
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
        except Exception as e:
            raise Exception("Error %s during cache call" %
                            (e.__class__.__name__,))
        return cached.doc.encode("utf-8")

    def store(self, host, path, params, doc, obj):
        Cache.objects.filter(
            host=host, path=path, params=repr(params)
            ).delete()
        # Ugly hack for bug #106748
        if hasattr(obj, 'cachedUntil'):
            cacheduntil = datetime.datetime.utcfromtimestamp(obj.cachedUntil)
        else:
            cacheduntil = datetime.datetime.utcfromtimestamp(obj.result.cachedUntil)
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

    class Meta:
        ordering = ["historydate", "typeid"]

class LastUpdated(models.Model):
    apitimestamp = models.DateTimeField()
    ownerid = models.BigIntegerField()
    methodname = models.CharField(max_length=255)

    class Meta:
        unique_together = (('ownerid', 'methodname'),)
        ordering = ["id"]

class Division(models.Model):
    apitimestamp = models.DateTimeField()
    ownerid = models.BigIntegerField()

    accountKey = models.IntegerField()
    hangarname = models.CharField(max_length=255)
    walletname = models.CharField(max_length=255)

    class Meta:
        unique_together = (('apitimestamp', 'ownerid', 'accountKey'),)
        ordering = ['ownerid', 'accountKey']

class Balance(models.Model):
    apitimestamp = models.DateTimeField()
    ownerid = models.BigIntegerField()

    accountID = models.BigIntegerField()
    accountKey = models.IntegerField()
    balance = models.DecimalField(max_digits=32, decimal_places=2)

    class Meta:
        unique_together = (('apitimestamp', 'ownerid', 'accountKey'),)
        ordering = ["ownerid", "accountKey"]

class Transaction(models.Model):
    apitimestamp = models.DateTimeField(db_index=True)
    ownerid = models.BigIntegerField(db_index=True)
    accountKey = models.IntegerField()

    transactionDateTime = models.DateTimeField(db_index=True)
    transactionID = models.BigIntegerField(unique=True, db_index=True)
    quantity = models.IntegerField()
    typeName = models.CharField(max_length=255)
    typeID = models.IntegerField()
    price = models.DecimalField(max_digits=32, decimal_places=2)
    clientID = models.BigIntegerField()
    clientName = models.CharField(max_length=255)
    stationID = models.IntegerField()
    stationName = models.CharField(max_length=255)
    transactionType = models.CharField(max_length=32)
    transactionFor = models.CharField(max_length=32)
    journalTransactionID = models.BigIntegerField()

    class Meta:
        ordering = ["transactionDateTime", "id"]

class Journal(models.Model):
    apitimestamp = models.DateTimeField(db_index=True)
    ownerid = models.BigIntegerField(db_index=True)
    accountKey = models.IntegerField()

    date = models.DateTimeField(db_index=True)
    refID = models.BigIntegerField(db_index=True)
    refTypeID = models.IntegerField()
    ownerName1 = models.CharField(max_length=255)
    ownerID1 = models.BigIntegerField()
    ownerName2 = models.CharField(max_length=255)
    ownerID2 = models.BigIntegerField()
    argName1 = models.CharField(max_length=255)
    argID1 = models.BigIntegerField()
    amount = models.DecimalField(max_digits=32, decimal_places=2)
    balance = models.DecimalField(max_digits=32, decimal_places=2)
    reason = models.CharField(max_length=255)
    taxReceiverID = models.BigIntegerField(null=True)
    taxAmount = models.DecimalField(max_digits=32, decimal_places=2, null=True)

    class Meta:
        ordering = ["date", "id"]

class Asset(models.Model):
    apitimestamp = models.DateTimeField(db_index=True)
    ownerid = models.BigIntegerField(db_index=True)

    itemID = models.BigIntegerField(db_index=True)
    typeID = models.IntegerField()
    locationID = models.BigIntegerField()
    flag = models.IntegerField()
    quantity = models.IntegerField()
    singleton = models.BooleanField()
    container = models.ForeignKey('self', null=True)

    @property
    def location(self):
        return InvItem(self.locationID)

    @property
    def type(self):
        return Type.objects.get(typeID=self.typeID)

    @property
    def flagobj(self):
        return Flag.objects.get(flagID=self.flag)

    class Meta:
        unique_together = (('apitimestamp', 'ownerid', 'itemID'),)
        ordering = ["id"]

class MarketOrder(models.Model):
    apitimestamp = models.DateTimeField(db_index=True)
    ownerid = models.BigIntegerField(db_index=True)

    orderID = models.BigIntegerField()
    charID = models.BigIntegerField()
    stationID = models.BigIntegerField()
    volEntered = models.IntegerField()
    volRemaining = models.IntegerField()
    minVolume = models.IntegerField()
    orderState = models.IntegerField()
    typeID = models.BigIntegerField()
    range = models.IntegerField()
    accountKey = models.IntegerField()
    duration = models.IntegerField()
    escrow = models.BigIntegerField()
    price = models.DecimalField(max_digits=32, decimal_places=2)
    bid = models.BooleanField()
    issued = models.DateTimeField()

class IndustryJob(models.Model):
    apitimestamp = models.DateTimeField(db_index=True)
    ownerid = models.BigIntegerField(db_index=True)

    jobID = models.BigIntegerField()
    assemblyLineID = models.BigIntegerField()
    containerItemID = models.BigIntegerField(null=True)
    installedItemID = models.BigIntegerField()
    installedItemLocationID = models.BigIntegerField()
    installedItemQuantity = models.IntegerField()
    installedItemProductivityLevel = models.IntegerField()
    installedItemMaterialLevel = models.IntegerField()
    installedItemLicensedProductionRunsRemaining = models.IntegerField()
    outputLocationID = models.BigIntegerField()
    runs = models.IntegerField()
    licensedProductionRuns = models.IntegerField()
    installedInSolarSystemID = models.BigIntegerField()
    containerLocationID = models.BigIntegerField()
    materialMultiplier = models.FloatField()
    charMaterialMultiplier = models.FloatField()
    timeMultiplier = models.FloatField()
    charTimeMultiplier = models.FloatField()
    installedItemTypeID = models.IntegerField()
    outputTypeID = models.IntegerField()
    containerTypeID = models.IntegerField()
    installedItemCopy = models.BooleanField()
    completed = models.BooleanField()
    completedSuccessfully = models.BooleanField()
    installedItemFlag = models.IntegerField()
    outputFlag = models.IntegerField()
    activityID = models.IntegerField()
    completedStatus = models.IntegerField()
    installTime = models.DateTimeField()
    beginProductionTime = models.DateTimeField()
    endProductionTime = models.DateTimeField()
    pauseProductionTime = models.DateTimeField()
