import base64
import hashlib
import os
import time

class FileCache(object):
    def __init__(self, dir):
        self.dir = dir

    def retrieve(self, host, path, params):
        fname = self.get_file_name(host, path, params)
        try:
            f = file(fname)
        except Exception:
            return None
        cached_until = int(f.readline())
        if time.mktime(time.gmtime()) > cached_until:
            os.unlink(fname)
            return None
        else:
            return f

    def store(self, host, path, params, doc, obj):
        f = file(self.get_file_name(host, path, params), "w")
        f.write("%i\n" % obj.cachedUntil)
        f.write(doc)
        f.close()

    def get_file_name(self, host, path, params):
        p = params.items()
        p.sort()
        pstring = "&".join(["%s=%s" % (base64.b64encode(str(a)),
                                       base64.b64encode(str(b)))
                            for (a, b) in p])
        fname = hashlib.md5("%s&%s&%s" % (base64.b64encode(host),
                                          base64.b64encode(path),
                                          base64.b64encode(pstring))).hexdigest()
        return os.path.join(self.dir, fname)
