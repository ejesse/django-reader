from django.conf.urls.defaults import *
from reader.views import markRead, getFeed, updateFeed

urlpatterns = patterns('',

    (r'^markRead/(?P<pk>\d{1,10})/$', markRead),
    (r'^getFeed/(?P<pk>\d{1,10})/$', getFeed),
    (r'^updateFeed/(?P<pk>\d{1,10})/$', updateFeed),
)