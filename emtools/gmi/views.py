import csv
import datetime
import json
import StringIO
import xml.etree.ElementTree as ET

from django.http import HttpResponse
from django.db import transaction, connection
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.list_detail import object_list
from django.views.generic.simple import direct_to_template

from emtools.emauth.decorators import require_mybbgroup
from emtools.ccpeve.models import MarketHistory
from emtools.ccpeve.ccpdb import get_typeid
from emtools.emauth.models import AuthToken
from emtools.gmi.models import Upload, Index
from emtools.gmi.index import TYPE_DATA

def view_index(request):
    if hasattr(request.user, 'profile') and 'Electus Matari' in request.user.profile.mybb_groups:
        is_internal = True
    else:
        is_internal = False
    index = dict((index.latest.typename, index.latest)
                 for index in Index.objects.all())
    index_table = []
    for typename, rowtype in TYPE_DATA:
        if rowtype == 'header':
            index_table.append({'row': 'header',
                                'header': typename})
        else:
            index_table.append({'row': 'entry',
                                'typename': typename,
                                'entry': index[typename]})
    format = request.GET.get('format', 'html')
    if format == 'csv':
        return view_csv(request, index_table)
    elif format == 'xml':
        return view_xml(request, index)
    else:
        return direct_to_template(request, 'gmi/index.html',
                                  extra_context={'tab': 'index',
                                                 'internal': is_internal,
                                                 'index_table': index_table})

def view_csv(request, index_table):
    out = StringIO.StringIO()
    writer = csv.writer(out)
    first = True
    for row in index_table:
        if row['row'] == 'header':
            if first:
                writer.writerow(['Typename', 'Index', 'Change', 'Volume',
                                 'Heimatar', 'Metropolis', 'Molden Heath',
                                 'Jita'])
                first = False
            else:
                writer.writerow([''] * 8)
            writer.writerow([row['header']] + [''] * 7)
        elif row:
            writer.writerow([row['typename'],
                             "%.2f" % row['entry'].republic,
                             "%+.2f%%" % ((row['entry'].republicchange-1) * 100),
                             row['entry'].republicvolume,
                             "%.2f" % row['entry'].heimatar,
                             "%.2f" % row['entry'].metropolis,
                             "%.2f" % row['entry'].moldenheath,
                             "%.2f" % row['entry'].jita])
    out.seek(0)
    return HttpResponse(out.read(),
                        status=200, mimetype="text/plain")

def view_xml(request, index):
    root = ET.Element("index")
    timestamp = None
    for typename, entry in index.items():
        typeelt = ET.SubElement(root, "type")
        timestamp = entry.timestamp
        typeelt.set("name", typename)
        typeelt.set("typeid", str(entry.typeid))
        typeelt.set("republic", str(entry.republic))
        typeelt.set("republicvolume", str(entry.republicvolume))
        typeelt.set("republicchange", str(entry.republicchange))
        typeelt.set("heimatar", str(entry.heimatar))
        typeelt.set("heimatarvolume", str(entry.heimatarvolume))
        typeelt.set("heimatarchange", str(entry.heimatarchange))
        typeelt.set("metropolis", str(entry.metropolis))
        typeelt.set("metropolisvolume", str(entry.metropolisvolume))
        typeelt.set("metropolischange", str(entry.metropolischange))
        typeelt.set("moldenheath", str(entry.moldenheath))
        typeelt.set("moldenheathvolume", str(entry.moldenheathvolume))
        typeelt.set("moldenheathchange", str(entry.moldenheathchange))
        typeelt.set("jita", str(entry.jita))
        typeelt.set("jitavolume", str(entry.jitavolume))
        typeelt.set("jitachange", str(entry.jitachange))
    root.set("timestamp", timestamp.strftime("%Y-%m-%d"))
    tree = ET.ElementTree(root)
    out = StringIO.StringIO()
    tree.write(out)
    out.seek(0)
    return HttpResponse(out.read(),
                        status=200, mimetype="text/xml")

def view_calculator(request):
    if hasattr(request.user, 'profile') and 'Electus Matari' in request.user.profile.mybb_groups:
        is_internal = True
    else:
        is_internal = False
    index = dict((index.latest.typename, index.latest.republic)
                 for index in Index.objects.all())
    prices = []
    for typename, rowtype in TYPE_DATA:
        if rowtype != 'header':
            prices.append((typename, index[typename]))
    return direct_to_template(request, 'gmi/calculator.html',
                              extra_context={'tab': 'calculator',
                                             'internal': is_internal,
                                             'jsondata': json.dumps(prices)})

@require_mybbgroup('Electus Matari')
def view_uploads(request):
    c = connection.cursor()
    c.execute("SELECT COUNT(*) AS uploadcount, "
              "       p.mybb_username "
              "FROM gmi_upload u "
              "     INNER JOIN emauth_profile p ON u.user_id = p.user_id "
              "WHERE u.timestamp >= NOW() - INTERVAL '28 days' "
              "GROUP BY p.mybb_username "
              "ORDER BY uploadcount DESC "
              "LIMIT 10")
    top10 = [{'rank': rank + 1, 'uploadcount': uploadcount, 'name': name}
             for (rank, (uploadcount, name)) in enumerate(c.fetchall())]
    return object_list(request, Upload.objects.filter(user=request.user),
                       paginate_by=20,
                       template_name='gmi/uploads.html',
                       extra_context={'tab': 'uploads',
                                      'internal': True,
                                      'top10': top10},
                       template_object_name='upload')

@require_mybbgroup('Electus Matari')
def view_uploader(request):
    if hasattr(request.user, 'profile') and 'Electus Matari' in request.user.profile.mybb_groups:
        is_internal = True
    else:
        is_internal = False
    return direct_to_template(request, 'gmi/uploader.html',
                              extra_context={'tab': 'uploader',
                                             'internal': is_internal})

@require_mybbgroup('Electus Matari')
def view_autoupload(request):
    if hasattr(request.user, 'profile') and 'Electus Matari' in request.user.profile.mybb_groups:
        is_internal = True
    else:
        is_internal = False
    region = request.GET.get('region', None)
    typeids = set()
    for typename, rowtype in TYPE_DATA:
        if rowtype != 'header':
            typeids.add(get_typeid(typename))
    typeids = sorted(typeids)
    return direct_to_template(request, 'gmi/autoupload.html',
                              extra_context={'tab': 'autoupload',
                                             'jsondata': json.dumps(typeids),
                                             'internal': is_internal})

##################################################################
# Cache file parsing

MAXSIZE = 5 * 1024 * 1024

from reverence.blue import marshal

def view_checktoken(request, token):
    try:
        authtoken = AuthToken.objects.get(token=token)
        return HttpResponse(authtoken.user.profile.mybb_username,
                            status=200, mimetype="text/plain")
    except AuthToken.DoesNotExist:
        return HttpResponse('Bad authentication token',
                            status=403, mimetype="text/plain")

@transaction.commit_manually
@csrf_exempt
def view_submit(request, token):
    try:
        authtoken = AuthToken.objects.get(token=token)
        user = authtoken.user
    except AuthToken.DoesNotExist:
        return HttpResponse('Bad authentication token',
                            status=403, mimetype="text/plain")

    data = request.raw_post_data
    if len(data) <= 30:
        return HttpResponse("Data too short",
                            status=415, mimetype="text/plain")
    if len(data) > MAXSIZE:
        return HttpResponse("Data too large",
                            status=415, mimetype="text/plain")
    if data[0] != '\x7e':
        return HttpResponse("Magic marker missing",
                            status=415, mimetype="text/plain")
    if data[12:30] != 'GetOldPriceHistory':
        return HttpResponse("Unknown cache file",
                            status=415, mimetype="text/plain")

    try:
        count = 0
        parsed = marshal.Load(data)
        regionid = parsed[0][2]
        typeid = parsed[0][3]
        lastdate = None
        for row in parsed[1]['lret']:
            historydate = wintime_to_datetime(row.historyDate)
            if lastdate is None or historydate > lastdate:
                lastdate = historydate
            obj, created = MarketHistory.objects.get_or_create(
                regionid=regionid,
                typeid=typeid,
                historydate=historydate,
                defaults={'lowprice': row.lowPrice,
                          'highprice': row.highPrice,
                          'avgprice': row.avgPrice,
                          'volume': row.volume,
                          'orders': row.orders})
            if created:
                count += 1
        Upload.objects.get_or_create(
            user=user,
            regionid=regionid,
            typeid=typeid,
            calltimestamp=wintime_to_datetime(parsed[1]['version'][0]))
        transaction.commit()
        return HttpResponse("Successfully added %i entries" % count,
                            status=200, mimetype="text/plain")
    except Exception:
        transaction.rollback()
        import traceback
        return HttpResponse("Error parsing the cache file: %s" % traceback.format_exc(),
                            status=415, mimetype="text/plain")


def wintime_to_datetime(timestamp):
    return datetime.datetime.utcfromtimestamp(
        (timestamp - 116444736000000000L) / 10000000
        )
