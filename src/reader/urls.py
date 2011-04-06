from django.conf.urls.defaults import *
from reader.views import mark_read, get_feed, update_feed

urlpatterns = patterns('',

    (r'^markRead/(?P<pk>\d{1,10})/$', mark_read),
    (r'^feeds/(?P<url>/$', get_feed),
    (r'^updateFeed/(?P<pk>\d{1,10})/$', update_feed),
)