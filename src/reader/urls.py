from django.conf.urls.defaults import *
from reader.views import my_entries,feeds

urlpatterns = patterns('',
    url(r'^my/$', my_entries, name="my_entries"),
    url(r'^feeds/$', feeds, name="feeds"),
)