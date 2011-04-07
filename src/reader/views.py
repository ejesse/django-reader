from django import views
from reader.forms import FeedForm
from reader.models import Feed, FeedEntry, Category, UserCategory, UserEntry, UserFeed, DEFAULT_CATEGORY_SLUG
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

@login_required
def my_entries(request):
    user = request.user
    try:
        user_feed = UserFeed.objects.get(user=request.user)
    except UserFeed.DoesNotExist:
        ##todo fixme we should auto create a feed
        ## and send the user to some sort of get started thing
        pass
    
    template = 'aggregated_feed.html'
    context = RequestContext(request)
    entries = UserEntry.objects.filter(user=user)
    context['entries'] = entries
    return render_to_response(template,context)

@login_required
def add_feed(request):
    user = request.user
    if not request.POST:
        ##todo fixme respond correctly
        return None
    feed_url = request.POST['url']
    try:
        feed = Feed.objects.get(url=feed_url)
    except Feed.DoesNotExist:
        feed = Feed()
        feed.url = feed_url
        feed.save()
    try:
        category_slug=request.POST['category']
        base_category = Category.objects.get(category_slug=category_slug)
        category = UserCategory.objects.get(category=base_category,user=user)
    except:
        default_category = Category.objects.get(category_slug=DEFAULT_CATEGORY_SLUG)
        category = UserCategory.objects.get(category=default_category,user=user)
    category.feeds.add(feed)
    category.save()
    feed.fetch()
    return HttpResponseRedirect(reverse('my_entries'))

def feeds(request):
    if request.POST is not None:
        return add_feed(request)
    return None
    
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