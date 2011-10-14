import datetime

from django.db import connection
from emtools.gmi.index import TYPE_DATA, REFINEABLES_DATA

def upload_age(regionid, typeid):
    c = connection.cursor()
    c.execute("SELECT MAX(calltimestamp) "
              "FROM gmi_upload "
              "WHERE regionid = %s "
              "  AND typeid = %s",
              (regionid, typeid))
    ts = c.fetchone()[0]
    if ts is None:
        return 367
    delta = datetime.datetime.utcnow().date() - ts.date()
    return delta.days # We round down
