from django.conf.urls.defaults import *
from reader.views import *

urlpatterns = patterns('',
    (r'^my/$', my_entries),
)