import datetime

# Can't use etree as attribute order is relevant. Not joking.
from xml.sax.saxutils import escape, quoteattr

def api_error(fobj, code, text, version=2):
    now = datetime.datetime.utcnow()
    then = now + datetime.timedelta(hours=12)
    fobj.write("""<eveapi version=%s>
  <currentTime>%s</currentTime>
  <error code=%s>%s</error>
  <cachedUntil>%s</cachedUntil>
</eveapi>
""" % (quoteattr(str(version)),
       now.strftime("%Y-%m-%d %H:%M:%S"),
       quoteattr(str(code)),
       escape(text),
       then.strftime("%Y-%m-%d %H:%M:%S")))

class APIResult(object):
    def __init__(self, version=2, currentTime=None, cachedUntil=None,
                 cached_hours=1):
        self.version = version
        if currentTime is not None:
            self.currentTime = currentTime
        else:
            self.currentTime = datetime.datetime.utcnow()
        if cachedUntil is not None:
            self.cachedUntil = cachedUntil
        else:
            self.cachedUntil = (datetime.datetime.utcnow() +
                                datetime.timedelta(hours=cached_hours))
        self.result = []
        self.error = None

    def add_value(self, name, value):
        self.result.append(('value', name, value))

    def add_rowset(self, name, columns, key=None):
        self.result.append(('rowset', name, (columns, key, [])))

    def add_row(self, columns):
        self.result[-1][2][2].append(columns)

    def writexml(self, fobj):
        fobj.write("""<eveapi version=%s>
  <currentTime>%s</currentTime>
  <result>
""" % (quoteattr(str(self.version)),
       self.currentTime.strftime("%Y-%m-%d %H:%M:%S")))

        for what, name, value in self.result:
            if what == 'value':
                fobj.write("    <%s>%s</%s>\n" %
                           (name, escape(str(value)), name))
            elif what == 'rowset':
                columns, key, rows = value
                if key is None:
                    fobj.write('    <rowset name=%s columns=%s>\n' %
                               (quoteattr(str(name)),
                                quoteattr(",".join(str(x) for x in columns))))
                else:
                    fobj.write('    <rowset name=%s key=%s columns=%s>\n' %
                               (quoteattr(str(name)), quoteattr(str(key)),
                                quoteattr(",".join(str(x) for x in columns))))
                for row in rows:
                    fobj.write("      <row")
                    for colname, colvalue in row:
                        fobj.write(" %s=%s" % (colname,
                                               quoteattr(str(colvalue))))
                    fobj.write("/>\n")
                fobj.write('    </rowset>\n')
        fobj.write("  </result>\n")
        fobj.write("  <cachedUntil>%s</cachedUntil>\n" %
                   self.cachedUntil.strftime("%Y-%m-%d %H:%M:%S"))
        fobj.write("</eveapi>\n")
