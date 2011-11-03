import datetime
import json
import re
import time

from django.http import HttpResponse

from emtools.utils import connect

OP_SUBJECT_RX = re.compile(
    r"^(\d+\.\d{2}\.\d{2}).*\| *(\d\d?:\d{2}) *\|(?: *([^|]*\S) *\|)? *(.*)"
    )

FID_EM = 111
FID_GRD = 144
FID_LUTI = 145
FID_ALLY = 149
def json_notifications(request):
    if ((not request.user.is_authenticated() or 
         request.user.profile.characterid is None)):
        return HttpResponse(json.dumps([]), mimetype="text/javascript")
    fid_list = []
    if 'Ally' in request.user.profile.mybb_groups:
        fid_list.append(FID_ALLY)
    if 'Lutinari Syndicate' in request.user.profile.mybb_groups:
        fid_list.append(FID_LUTI)
    if 'Gradient' in request.user.profile.mybb_groups:
        fid_list.append(FID_GRD)
    if 'Electus Matari' in request.user.profile.mybb_groups:
        fid_list.append(FID_EM)
        fid_list.append(FID_ALLY)
    now = datetime.datetime.utcnow()
    today = "%s.%02i.%02i" % (now.year - 1898, now.month, now.day)
    conn = connect('emforum')
    c = conn.cursor()
    c.execute("SELECT tid, username, subject "
              "FROM mybb_threads "
              "WHERE fid in (%s) "
              "  AND NOT sticky "
              "  AND subject REGEXP '^[0-9]+\\.[0-9]{2}\\.[0-9]{2}' "
              "  AND subject >= %%s"
              % (", ".join(str(fid) for fid in fid_list),),
              (today,))
    result = []
    for tid, username, subject in c.fetchall():
        m = OP_SUBJECT_RX.match(subject)
        if m is None:
            continue
        year, month, day = (int(x) for x in m.group(1).split("."))
        hour, minute = (int(x) for x in m.group(2).split(":"))
        dt = datetime.datetime(year + 1898, month, day, hour, minute)
        timestamp = time.mktime(dt.timetuple())
        location = m.group(3)
        text = m.group(4)
        result.append({'url': 'http://www.electusmatari.com/forums/showthread.php?tid=%s' % (tid,),
                       'tid': tid,
                       'username': username,
                       'time': int(timestamp),
                       'location': location,
                       'text': text})
    result.sort(key=lambda obj: obj['time'])
    return HttpResponse(json.dumps(result), mimetype="text/json")

def test(request):
    return HttpResponse("""
<html>
 <body>
<script type="text/javascript">
  var cookieDomain = ".electusmatari.com";
  var cookiePath = "/";
  var cookiePrefix = "";
</script>
<script type="text/javascript" src="http://www.electusmatari.com/forums/jscripts/prototype.js?ver=1603"></script>
<script type="text/javascript" src="http://www.electusmatari.com/forums/jscripts/general.js?ver=1603"></script>
<script type="text/javascript" src="/media/js/notifications.js"></script>
 </body>
 <div id="debug"></div>
</html>
""",
                        mimetype="text/html")
