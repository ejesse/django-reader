from django.db import models

import feedparser
import md5

class Feed(models.Model):
    name = models.CharField(max_length=100)
    url = models.URLField(unique=True)
    
    def fetch(self):
        newEntryList = []
        list = feedparser.parse(self.url)
        self.save()
        for entry in list.entries:
            newEntry = FeedEntry(title = entry.title,
                                 link = entry.link,
                                 feed = self,
                                 description = entry.description,
                                 read = False,
                                )
            if newEntry.exists():
                newEntryList.append(newEntry)
        return newEntryList
        
    def unread(self):
        """ Return number of unread entries for the feed """
        unread = FeedEntry.objects.filter(feed=self, read = False)
        return len(unread) 

    def __unicode__(self):
        return self.name

class FeedEntry(models.Model):
    feed = models.ForeignKey(Feed)
    link = models.URLField(unique=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    read = models.BooleanField()
    updated = models.BooleanField()
    date = models.DateTimeField(blank=True,null=True)

    def exists(self):
        try:
            self.save()
            return True
        except:
            return False
            
    def markRead(self):
        self.read = True
        self.save()

    def __unicode__(self):
        return self.title


