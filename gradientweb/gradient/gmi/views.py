import csv
import json
import StringIO
import xml.etree.ElementTree as ET

from django.http import HttpResponse
from django.views.generic.simple import direct_to_template

from emtools.gmi.index import TYPE_DATA, REFINEABLES_DATA

from models import Index

def index(request):
    index = dict((index.latest.typename, index.latest)
                 for index in Index.objects.all())
    index_table = []
    for typename, rowtype in TYPE_DATA + REFINEABLES_DATA:
        if rowtype == 'header':
            index_table.append({'row': 'header',
                                'name': typename})
        else:
            index_table.append({'row': 'entry',
                                'typename': typename,
                                'entry': index[typename]})
    format = request.GET.get('format', 'html')
    if format == 'csv':
        return index_csv(request, index_table)
    elif format == 'xml':
        return index_xml(request, index)
    else:
        return direct_to_template(request, 'gmi/index.html',
                                  extra_context={'index_table': index_table})

def index_csv(request, index_table):
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
            writer.writerow([row['name']] + [''] * 7)
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

def index_xml(request, index):
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

def calculator(request):
    index = dict((index.latest.typename, index.latest.republic)
                 for index in Index.objects.all())
    prices = []
    lastheader = 'Unknown'
    for typename, rowtype in TYPE_DATA + REFINEABLES_DATA:
        if rowtype != 'header':
            prices.append({'name': typename,
                           'value': index[typename],
                           'type': lastheader})
        else:
            lastheader = typename
    return direct_to_template(request, 'gmi/calculator.html',
                              extra_context={'jsondata': json.dumps(prices)})
