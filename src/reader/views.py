from django import views
from reader.forms import FeedForm
from reader.models import Feed, FeedEntry, Category, UserCategory, UserEntry, UserFeed
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.shortcuts import render_to_response
from django.template.context import RequestContext

def my_entries(request):
    user = request.user
    if not user.is_authenticated:
        ## todo fixme make this an unauth error
        return None
    template = 'aggregated_feed.html'
    context = RequestContext(request)
    entries = UserEntry.objects.filter(user=user)
    context['entries'] = entries
    return render_to_response(template,context)

    
def mark_read(request, pk):
    state = ''
    try:
        markEntry = FeedEntry.objects.get(pk=pk)
        markEntry.markRead()
        state = 'ok'
    except:
        state = 'error'
    if request.is_ajax():
        return ajax_response(state)
    
def update_feed(request, pk,
               template_name='feedlist.html'):
    try:
        rssFeed = Feed.objects.get(pk=pk)
        context = {}
        context['FeedList'] = rssFeed.fetch()
        state = 'ok'
    except:
        state = 'error'
    if request.is_ajax():
        return ajax_response(state, context, template_name) 

def get_feed(request, pk,
            template_name='feedlist.html'):
    try:
        feedObj = Feed.objects.get(pk=pk)
        feedList = FeedEntry.objects.filter(feed=feedObj)
        context = {}
        context['FeedList'] = feedList
        context['FeedName'] = feedObj.name
        state = 'ok'
    except:
        state = 'error'
    if request.is_ajax():
        return ajax_response(state, context, template_name) 

def ajax_response(state, context=None, template=None):
    if context != None:
        return render_to_response(template, context)
    if state == 'ok':
        return HttpResponse('')
    else:
        return HttpResponse(status=500)