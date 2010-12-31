import datetime

from emtools.intel.views import update_all

SCHEDULE = [('intel-update', update_all, 60*12)]
