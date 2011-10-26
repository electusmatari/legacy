import datetime

from gradient import dbutils
from gradient.uploader.models import MarketHistory
from gradient.index.models import Index, IndexHistory

def update_index():
    for idx in Index.objects.all():
        if idx.refineable:
            continue
        idxh = IndexHistory()
        idxh.typeid = idx.typeid
        # Heimatar
        price, volume, age = get_region_index(idx.typeid, dbutils.HEIMATAR)
        idxh.heimatarchange = idx.heimatarchange = price - idx.heimatar
        idxh.heimatar = idx.heimatar = price
        idxh.heimatarvolume = idx.heimatarvolume = volume
        idxh.heimatarage = idx.heimatarage = age
        # Metropolis
        price, volume, age = get_region_index(idx.typeid, dbutils.METROPOLIS)
        idxh.metropolischange = idx.metropolischange = price - idx.metropolis
        idxh.metropolis = idx.metropolis = price
        idxh.metropolisvolume = idx.metropolisvolume = volume
        idxh.metropolisage = idx.metropolisage = age
        # Molden Heath
        price, volume, age = get_region_index(idx.typeid, dbutils.MOLDENHEATH)
        idxh.moldenheathchange = idx.moldenheathchange = (price -
                                                          idx.moldenheath)
        idxh.moldenheath = idx.moldenheath = price
        idxh.moldenheathvolume = idx.moldenheathvolume = volume
        idxh.moldenheathage = idx.moldenheathage = age
        # The Forge
        price, volume, age = get_region_index(idx.typeid, dbutils.THEFORGE)
        idxh.jitachange = idx.jitachange = price - idx.jita
        idxh.jita = idx.jita = price
        idxh.jitavolume = idx.jitavolume = volume
        idxh.jitaage = idx.jitaage = age
        # Republic
        price, volume = get_republic_index(idx)
        idxh.republicchange = idx.republicchange = price - idx.republic
        idxh.republic = idx.republic = price
        idxh.republicvolume = idx.republicvolume = volume
        # Done
        idx.save()
        idxh.save()
    for idx in Index.objects.all():
        if not idx.refineable:
            continue
        idxh = IndexHistory()
        idxh.typeid = idx.typeid
        update_refineable(idx, idxh)
        idx.save()
        idxh.save()

def get_region_index(typeid, regionid):
    # Price is the average price of the last 7 days with transactions
    # Volume is the volume in the last 7 days, even with losses of days
    # Age is the age of the first transaction we find
    now = datetime.datetime.utcnow().date()
    oneweekago = (datetime.datetime.utcnow() - datetime.timedelta(days=7)
                  ).date()
    totalvolume = 0
    totalcost = 0
    volume7d = 0
    firstdate = None
    for mh in MarketHistory.objects.filter(typeid=typeid, regionid=regionid
                                           ).order_by("-historydate")[0:7]:
        if firstdate is None:
            firstdate = mh.historydate
        totalvolume += mh.volume
        totalcost += mh.avgprice * mh.volume
        if mh.historydate >= oneweekago:
            volume7d += mh.volume
    if totalvolume > 0:
        price = totalcost / totalvolume
    else:
        price = 0.0
    volume = volume7d
    if firstdate is None:
        age = 367
    else:
        age = (now - firstdate).days
    return price, volume, age

def get_republic_index(idx):
    # Average price of the regions

    # This uses the average price of the last 7 transaction days and
    # the volume of the last 7 days, penalizing regions with non-daily
    # transactions.
    totalcost = (idx.heimatar * idx.heimatarvolume +
                 idx.metropolis * idx.metropolisvolume +
                 idx.moldenheath * idx.moldenheathvolume)
    volume = (idx.heimatarvolume +
              idx.metropolisvolume +
              idx.moldenheathvolume)
    # If the Republic does more than 1% of the volume in Jita, use our
    # own price. Else, simply use Jita.
    if volume > idx.jitavolume * 0.01:
        price = totalcost / volume
    else:
        price = idx.jita
    return price, volume

def update_refineable(idx, idxh):
    price = 0
    heimatarprice = 0
    metropolisprice = 0
    moldenheathprice = 0
    jitaprice = 0
    try:
        for typeid, quantity in dbutils.reprocess(idx.typeid):
            material = Index.objects.get(typeid=typeid)
            price += quantity * material.republic
            heimatarprice += quantity * material.heimatar
            metropolisprice += quantity * material.metropolis
            moldenheathprice += quantity * material.moldenheath
            jitaprice += quantity * material.jita
    except Index.DoesNotExist:
        price = 0
        heimatarprice = 0
        metropolisprice = 0
        moldenheathprice = 0
        jitaprice = 0
    idxh.republicchange = idx.republicchange = price - idx.republic
    idxh.republic = idx.republic = price
    idxh.republicvolume = idx.republicvolume = 0
    idxh.heimatarchange = idx.heimatarchange = price - idx.heimatar
    idxh.heimatar = idx.heimatar = heimatarprice
    idxh.heimatarvolume = idx.heimatarvolume = 0
    idxh.heimatarage = idx.heimatarage = 0
    idxh.metropolischange = idx.metropolischange = price - idx.metropolis
    idxh.metropolis = idx.metropolis = metropolisprice
    idxh.metropolisvolume = idx.metropolisvolume = 0
    idxh.metropolisage = idx.metropolisage = 0
    idxh.moldenheathchange = idx.moldenheathchange = price - idx.moldenheath
    idxh.moldenheath = idx.moldenheath = moldenheathprice
    idxh.moldenheathvolume = idx.moldenheathvolume = 0
    idxh.moldenheathage = idx.moldenheathage = 0
    idxh.jitachange = idx.jitachange = price - idx.jita
    idxh.jita = idx.jita = jitaprice
    idxh.jitavolume = idx.jitavolume = 0
    idxh.jitaage = idx.jitaage = 0
