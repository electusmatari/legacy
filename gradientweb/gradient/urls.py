from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

from django.views.generic.simple import direct_to_template

urlpatterns = patterns('',
    (r'^gmi/', include('gradient.gmi.urls')),
    (r'^staticshop/', direct_to_template,
     {'template': 'shop/staticshop.html'}),
    (r'^shop/', include('gradient.shop.urls')),
    (r'^rc/', include('gradient.rc.urls')),
    (r'^industry/', include('gradient.industry.urls')),
    (r'^gts/', include('gradient.gts.urls')),
    (r'^', include('gradient.grdstatic.urls')),

    # Example:
    # (r'^gradient/', include('gradient.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)
