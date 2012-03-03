import csv

import emcom.gmi as gmi

LOCALFILE = "/home/forcer/public_html/eve/grd-pricelist.txt"

def prices():
    prices = gmi.current()
    prices.update(dict([(row[0], float(row[1]))
                        for row in csv.reader(file(LOCALFILE))]))
    return prices
