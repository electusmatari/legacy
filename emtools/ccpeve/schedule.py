import datetime

from emtools.ccpeve.models import Cache
from emtools.ccpeve.apifetch import get_api_data

def expire_cache():
    Cache.objects.filter(cacheduntil__lt=datetime.datetime.utcnow()).delete()

SCHEDULE = [("api-cache-expire", expire_cache, 60),
            ("api-fetch", get_api_data, 60)]
