import csv

import config

def get():
    conf = config.get()
    index = mmi()
    for opt in conf.options("Index"):
        index[opt] = conf.getfloat("Index", opt)
    return index

fname = "/home/forcer/public_html/eve/gmi/current.txt"

def mmi():
    return dict((x[0], float(x[1]))
                for x
                in list(csv.reader(file(fname)))[1:]
                if x[1] != '')
