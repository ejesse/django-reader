from django.test import TestCase
from django.test.client import Client

from reader.models import Feed, FeedEntry
from reader.forms import FeedForm
from reader.views import mark_read
from django.core.urlresolvers import reverse

import unittest, new, os, sys, glob, re, urllib, string, posixpath, time, codecs
import SimpleHTTPServer, BaseHTTPServer
from threading import *

import feedparser

_PORT = 8097 # not really configurable, must match hardcoded port in tests

class FeedParserTestRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    headers_re = re.compile(r"^Header:\s+([^:]+):(.+)$", re.MULTILINE)
    def send_head(self):
        """Send custom headers defined in test case
    
        Example:
        <!--
        Header:   Content-type: application/atom+xml
        Header:   X-Foo: bar
        -->
        """
        path = self.translate_path(self.path)
        headers = dict(self.headers_re.findall(open(path).read()))
        f = open(path, 'rb')
        headers.setdefault('Status', 200)
        self.send_response(int(headers['Status']))
        headers.setdefault('Content-type', self.guess_type(path))
        self.send_header("Content-type", headers['Content-type'])
        self.send_header("Content-Length", str(os.fstat(f.fileno())[6]))
        for k, v in headers.items():
            if k not in ('Status', 'Content-type'):
                self.send_header(k, v)
        self.end_headers()
        return f

    def log_request(self, *args):
        pass

class FeedParserTestServer(Thread):
    """HTTP Server that runs in a thread and handles a predetermined number of requests"""
  
    def __init__(self, requests):
        Thread.__init__(self)
        self.requests = requests
        self.ready = 0
    
    def run(self):
        self.httpd = BaseHTTPServer.HTTPServer(('', _PORT),
        				    FeedParserTestRequestHandler)
        self.ready = 1
        while self.requests:
            self.httpd.handle_request()
            self.requests -= 1

class FeedparserTests(TestCase):
    
    urls = 'reader.urls'
    
    def setUp(self):
        self.client = Client()
    
    def test_environment(self):
        """Just make sure everything is set up correctly."""
        self.assert_(True)
        try:
            import feedparser
        except:
            self.assert_(False)

    def test_double_update(self):
        """Check for no changes to model when rss is not changed"""
        httpd = FeedParserTestServer(2)
        httpd.start()
        rssUrl = 'http://localhost:8097/src/reader/test_rss/test_1.rss'
        tempRss = Feed(name="Craig's List Free", url=rssUrl)
        newEntry = tempRss.fetch()
        tempFeedList = FeedEntry.objects.all()
        self.assertEqual(len(tempFeedList), 100)
        self.assertEqual(len(newEntry), 100)
        tempFeedList = FeedEntry.objects.get(link='http://columbus.craigslist.org/zip/1326047327.html')
        self.assertEqual(tempFeedList.title, 'at the curb: dresser and small table (Royal Dornoch Cir. Delaware 43015)')
        newEntry = tempRss.fetch()
        tempFeedList = FeedEntry.objects.all()
        self.assertEqual(len(tempFeedList), 100)
        tempFeedList = FeedEntry.objects.get(link='http://columbus.craigslist.org/zip/1326047327.html')
        self.assertEqual(len(newEntry), 0)

    def test_changed_update(self):
        """Update and check for new entries"""
        httpd = FeedParserTestServer(2)
        httpd.start()
        rssUrl = 'http://localhost:8097/src/reader/test_rss/test_1.rss'
        tempRss = Feed(name="Craig's List Free", url=rssUrl)
        tempRss.fetch()
        rssUrl = 'http://localhost:8097/src/reader/test_rss/test_1_update.rss'
        tempRss = Feed(url=rssUrl)
        tempRss.save()
        newEntry = tempRss.fetch()
        tempFeedList = FeedEntry.objects.all()
        self.assertEqual(len(tempFeedList), 105)
        self.assertEqual(len(newEntry), 5)
        
    def test_read_functions(self):
        """ check read functions for an entry """
        httpd = FeedParserTestServer(1)
        httpd.start()
        rssUrl = 'http://localhost:8097/src/reader/test_rss/test_2.rss'
        tempRss = Feed(name="Temp", url=rssUrl)
        tempRss.fetch()
        self.assertEqual(tempRss.unread(), 1)
        entry = FeedEntry.objects.all()[0]     
        entry.markRead()
        self.assertEqual(tempRss.unread(), 0)

# View testing

    def test_view_ajax_mark_read(self):
        """ Test view for mark server """
        httpd = FeedParserTestServer(1)
        httpd.start()
        rssUrl = 'http://localhost:8097/src/reader/test_rss/test_2.rss'
        tempRss = Feed(name="Temp", url=rssUrl)
        tempRss.fetch()
        response = self.client.get('/markRead/1/',
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(tempRss.unread(), 0)  
        # bad request
        response = self.client.get('/markRead/10/',
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 500)
        
    def test_view_ajax_getFeed(self):
        """ Get Full Feed """
        httpd = FeedParserTestServer(1)
        httpd.start()
        rssUrl = 'http://localhost:8097/src/reader/test_rss/test_2.rss'
        tempRss = Feed(name="Temp", url=rssUrl)
        tempRss.fetch()
        tempRss.save()
        response = self.client.get('/getFeed/1/',
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        #print response.content
        self.assertEqual(len(response.context['FeedList']), 1)
        
    def test_view_ajax_updateFeed(self):
        """ Update partial feed """
        httpd = FeedParserTestServer(1)
        httpd.start()
        rssUrl = 'http://localhost:8097/src/reader/test_rss/test_2.rss'
        tempRss = Feed(name="Temp", url=rssUrl)
        tempRss.save()
        response = self.client.get('/updateFeed/1/',
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(len(response.context['FeedList']), 1)
        #print response.content