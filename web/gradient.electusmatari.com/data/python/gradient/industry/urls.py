from django.conf.urls.defaults import *

urlpatterns = patterns('gradient.industry.views',
  (r'^$', 'overview'),
  (r'^bpos/$', 'bpos_view'),
  (r'^bpos/(?P<bpoid>[0-9]+)/edit/$', 'bpos_edit'),
  (r'^bpos/(?P<bpoid>[0-9]+)/delete/$', 'bpos_delete'),
  (r'^bpos/create/$', 'bpos_edit'),
  (r'^prices/$', 'prices_view'),
  (r'^build/(?P<typename>[^/]*)/$', 'build_view'),
  (r'^marketorders/$', 'marketorders_view'),
  (r'^marketorders/(?P<orderid>[0-9]+)/edit/$', 'marketorders_edit'),
  (r'^marketorders/(?P<orderid>[0-9]+)/delete/$', 'marketorders_delete'),
  (r'^marketorders/create/$', 'marketorders_edit'),
  (r'^marketorders/config/$', 'config_view'),
  (r'^stocks/$', 'stocks_view'),
  (r'^stocks/watched/$', 'stocks_view', {'watched': True}),
  (r'^stocks/(?P<stockid>[0-9]+)/edit/$', 'stocks_edit'),
  (r'^stocks/(?P<stockid>[0-9]+)/delete/$', 'stocks_delete'),
  (r'^stocks/(?P<stockid>[0-9]+)/watch/$', 'stocks_watch'),
  (r'^stocks/(?P<stockid>[0-9]+)/unwatch/$', 'stocks_unwatch'),
  (r'^stocks/create/$', 'stocks_edit'),
  (r'^profitability/$', 'profitability'),
  (r'^autoupload/$', 'autoupload_view'),
  (r'^transactions/$', 'transactions_view'),
  (r'^json/autoupload/$', 'autoupload_json'),
  (r'^json/invtypes/$', 'json_invtype'),
  (r'^json/blueprints/$', 'json_blueprint'),
  (r'^json/stations/$', 'json_station'),
)
