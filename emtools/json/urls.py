from django.conf.urls.defaults import *

urlpatterns = patterns('emtools.operations.views',
    ('^json/$', 'json_notifications'),
    ('^$', 'test'),
)
