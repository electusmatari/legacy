from django.conf.urls.defaults import *

urlpatterns = patterns('emtools.fw.views',
    ('^$', 'view_topstats'),
)
