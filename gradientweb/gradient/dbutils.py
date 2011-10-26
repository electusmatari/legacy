from django.db import connection

THEFORGE = 10000002
MOLDENHEATH = 10000028
HEIMATAR = 10000030
METROPOLIS = 10000042

get_itemid
get_itemname
get_systemfaction


def reprocess(typeid):
    c = connection.cursor()
    c.execute("SELECT materialtypeid, quantity FROM ccp.invtypematerials "
              "WHERE typeid = %s", (typeid,))
    return c.fetchall()
