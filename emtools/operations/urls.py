from django.conf.urls.defaults import *

urlpatterns = patterns('emtools.operations.views',
    ('^xml/(?P<token>[A-Za-z0-9]+)/$', 'view_xml'),
)
