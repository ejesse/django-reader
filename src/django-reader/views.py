from django import views
from feedreader.forms import FeedForm
from feedreader.models import Feed, FeedEntry

from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import get_object_or_404, render_to_response


def markRead(request, pk):
    state = ''
    try:
        markEntry = FeedEntry.objects.get(pk=pk)
        markEntry.markRead()
        state = 'ok'
    except:
        state = 'error'
    if request.is_ajax():
        return ajax_response(state)
    
def updateFeed(request, pk,
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

def getFeed(request, pk,
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