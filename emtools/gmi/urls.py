from django.conf.urls.defaults import *

urlpatterns = patterns('emtools.gmi.views',
    ('^$', 'view_index'),
    ('^calculator/$', 'view_calculator'),
    ('^uploadhistory/$', 'view_uploads'),
    ('^uploader/$', 'view_uploader'),
    ('^autoupload/$', 'view_autoupload'),
    ('^submit/(?P<token>[A-Za-z0-9]+)/$', 'view_submit'),
    ('^checktoken/(?P<token>[A-Za-z0-9]+)/$', 'view_checktoken'),
)
