from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    (r'^reader/', include('reader.urls')),
    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
)
