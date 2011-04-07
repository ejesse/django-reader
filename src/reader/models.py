from django.db import models
from django.contrib.auth.models import User
from django_extensions.db.fields import AutoSlugField
from django.db.models.signals import post_save
from django.db.models.signals import post_syncdb
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

import datetime
from time import mktime
import feedparser

DEFAULT_CATEGORY = 'Uncategorized'
DEFAULT_CATEGORY_SLUG = 'uncategorized'

class Feed(models.Model):
    title = models.CharField(max_length=100,blank=True,null=True)
    url = models.URLField(unique=True)
    link = models.URLField(blank=True,null=True)
    description = models.TextField(blank=True,null=True)
    version = models.TextField(max_length=200,blank=True,null=True)
    encoding = models.TextField(max_length=200,blank=True,null=True)
    last_checked = models.DateTimeField(blank=True,null=True)
    
    def fetch(self):
        parsed_feed = feedparser.parse(self.url)
        self.title = parsed_feed.channel.title
        self.description = parsed_feed.channel.description
        self.link = parsed_feed.feed.link
        self.version = parsed_feed.version
        self.encoding = parsed_feed.encoding
        if not self.last_checked:
            self.last_checked = datetime.datetime(1980,1,1)
        self.save()
        for entry in parsed_feed.entries:
            entry_date = datetime.datetime.fromtimestamp(mktime(entry.date_parsed))
            entry_updated = datetime.datetime.fromtimestamp(mktime(entry.updated_parsed))
            if entry_updated > self.last_checked:
                updated = False
                new = False
                try:
                    feed_entry = FeedEntry.objects.get(link=entry.link)
                    if entry_updated > self.last_checked:
                        updated = True
                except FeedEntry.DoesNotExist:
                    new = True
                    feed_entry = FeedEntry()
                if updated or new:
                    feed_entry.feed = self
                    feed_entry.populate_from_parsed_feed_entry(entry)
                    feed_entry.save()
                if updated:
                    ## go mark all the items as unread for users
                    UserEntry.objects.filter(entry = feed_entry).update(read=False)
                if new:
                    ## go add to user's feeds
                    user_categories = UserCategory.objects.filter(feeds=self)
                    for user_cat in user_categories:
                        user_entry = UserEntry()
                        user_entry.user = user_cat.user
                        user_entry.entry = feed_entry
                        user_entry.save()
                    
        self.last_checked = datetime.datetime.now()
        self.save()
        
    def __unicode__(self):
        return self.title

class FeedEntry(models.Model):
    feed = models.ForeignKey(Feed)
    link = models.URLField(unique=True)
    title = models.CharField(max_length=250)
    author = models.CharField(max_length=250,null=True,blank=True)
    description = models.TextField(null=True,blank=True)
    summary_detail = models.TextField(null=True,blank=True)
    date_published = models.DateTimeField(blank=True,null=True)
    date_updated = models.DateTimeField(blank=True,null=True)

    def populate_from_parsed_feed_entry(self,feed_entry):
        self.link = feed_entry.link
        self.title = feed_entry.title
        try:
            self.author = feed_entry.author
        except:
            pass
        self.summary_detail = feed_entry.summary_detail.value
        try:
            self.description = feed_entry.description
        except:
            pass
        self.date_published = datetime.datetime.fromtimestamp(mktime(feed_entry.date_parsed))
        try:
            self.date_updated = datetime.datetime.fromtimestamp(mktime(feed_entry.updated_parsed))
        except:
            self.date_updated = self.date_published 

    def __unicode__(self):
        return self.title
    
    class Meta:
        ordering = ["-date_updated"]
        verbose_name_plural = "Feed Entries"

class Category(models.Model):
    category_name = models.CharField(max_length=200)
    category_slug = AutoSlugField(populate_from='category_name',unique=True)
    
    def __unicode__(self):
        return self.category_name
    
    class Meta:
        verbose_name_plural = "Categories"

class UserEntry(models.Model):
    user = models.ForeignKey(User)
    entry = models.ForeignKey(FeedEntry)
    read = models.BooleanField(default=False)
    
    def mark_as_read(self):
        if self.id:
            self.read=True
            self.save()
            
    def __unicode__(self):
        return "%s - %s" % (self.user, self.entry)

    class Meta:
        verbose_name_plural = "User Entries"
        ordering = ['entry']

class UserCategory(models.Model):
    user = models.ForeignKey(User)
    category = models.ForeignKey(Category)
    feeds = models.ManyToManyField(Feed,null=True,blank=True)
    
    def get_count_unread_entries(self):
        entries_for_category = FeedEntry.objects.filter(feed__in=self.feeds.all())
        return UserEntry.objects.filter(user=self.user,read=False,entry__in=entries_for_category).count()
    
    def get_unread_entries(self):
        ## this cant be the best way to do this...
        entries_for_category = FeedEntry.objects.filter(feed__in=self.feeds.all())
        return UserEntry.objects.filter(user=self.user,read=False,entry__in=entries_for_category)

    def __unicode__(self):
        return "%s - %s" % (self.user,self.category)

    class Meta:
        verbose_name_plural = "User Categories"
        
class UserFeed(models.Model):
    user = models.ForeignKey(User)
    is_public=models.BooleanField(default=False)
    categories = models.ManyToManyField(UserCategory,null=True,blank=True)
    
    def get_unread_entries(self):
        return UserEntry.objects.filter(user=self.user,read=False)
    
    def __unicode__(self):
        return self.user.__unicode__()

@receiver(post_save, sender=UserFeed)
def give_feed_default_category(sender, instance, signal, *args, **kwargs):
    if len(instance.categories.all()) < 1:
        default_category = Category.objects.get(category_slug=DEFAULT_CATEGORY_SLUG)
        try:
            user_default_category = UserCategory.objects.get(user=instance.user,category=default_category)
        except UserCategory.DoesNotExist:
            user_default_category = UserCategory()
            user_default_category.user = instance.user
            user_default_category.category = default_category
            user_default_category.save()
        categories = [user_default_category]
        instance.categories = categories
        instance.save()
    
@receiver(m2m_changed, sender=UserCategory.feeds.through)
def update_user_entries(sender, instance, signal, *args, **kwargs):
    user = instance.user
    feeds = instance.feeds.all()
    for feed in feeds:
        feed_entries = FeedEntry.objects.filter(feed=feed)[:20]
        for entry in feed_entries:
            try:
                user_entry = UserEntry.objects.get(entry=entry,user=user)
            except UserEntry.DoesNotExist:
                user_entry = UserEntry()
                user_entry.user = user
                user_entry.entry = entry
                user_entry.save()

@receiver(post_syncdb)
def bootstrap_data(sender, *args, **kwargs):
    print 'checking reader app bootstrap data'
    try:
        category = Category.objects.get(category_slug = DEFAULT_CATEGORY_SLUG)
    except Category.DoesNotExist:
        print 'populating default category'
        category = Category()
        category.category_name = DEFAULT_CATEGORY
        category.save()
    print 'done!'