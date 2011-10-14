from django.conf.urls.defaults import *

from django.views.generic.simple import direct_to_template

urlpatterns = patterns('gradient.gmi.views',
  (r'^$', 'index'),
  (r'^calculator/$', 'calculator'),
  (r'^help/$', direct_to_template, {'template': 'gmi/help.html'}),
)
