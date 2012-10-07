# Bulkdata loader

import sys
sys.path.append("/home/forcer/Programs/Reverence/active/lib64/python2.6/site-packages/")

import os

from reverence import blue

def load(dir, name):
    filename = blue.cache.GetCacheFileName(name)
    fullname = os.path.join(dir, "bulkdata", filename)
    data = blue.marshal.Load(file(fullname).read())
    if data[0] != name:
        raise RuntimeError, ('Unexpected bulkdata, expected %r, got %r.' %
                             (name, data[0]))
    return data[1].GetCachedObject()

def load(dirname):


    result = {}
    bd_dirname = os.path.join(dirname, "bulkdata")
    for filename in os.listdir(bd_dirname):
        fullname = os.path.join(bd_dirname, filename)
        (name, data) = blue.marshal.Load(file(fullname).read())
        result[name] = data
    return result
