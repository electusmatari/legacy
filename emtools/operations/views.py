import xml.etree.ElementTree as ET

from django.http import HttpResponse

from emtools import utils
from emtools.emauth.models import AuthToken

def view_xml(request, token):
    try:
        authtoken = AuthToken.objects.get(token=token)
        user = authtoken.user
    except AuthToken.DoesNotExist:
        return HttpResponse('Bad authentication token',
                            status=403, mimetype="text/plain")

    conn = utils.connect('emforum')
    c = conn.cursor()
    c.execute("SELECT u.username, o.start, o.description "
              "FROM mybb_ongoing_operations o "
              "     INNER JOIN mybb_users u ON o.uid = u.uid "
              "WHERE o.active "
              "  AND (UNIX_TIMESTAMP(NOW()) - UNIX_TIMESTAMP(o.start)) "
              "      <= (60*60) "
              "ORDER BY o.start ASC")
    root = ET.Element('operations')
    for username, start, description in c.fetchall():
        op = ET.SubElement(root, 'operation')
        op.set("username", username)
        op.set("start", start.strftime("%Y-%m-%dT%H:%M:%SZ"))
        op.set("created", start.strftime("%Y-%m-%dT%H:%M:%SZ"))
        op.text = description
    return HttpResponse(ET.tostring(root),
                        status=200,
                        mimetype="text/xml")
