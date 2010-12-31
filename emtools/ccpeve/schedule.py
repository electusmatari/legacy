import datetime

from emtools.ccpeve.models import Cache

def expire_cache():
    Cache.objects.filter(cacheduntil__lt=datetime.datetime.utcnow()).delete()

SCHEDULE = [("api-cache-expire", expire_cache, 60)]
