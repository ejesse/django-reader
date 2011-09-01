from celery.task.sets import TaskSet
from celery.task import task
from celery.task.sets import subtask
from reader.models import Feed
import logging

@task
def fetch_feed(feed_id,callback=None):
    feed = Feed.objects.get(id=feed_id)
    logging.warn("fetching feed %s" % (feed.title))
    feed.fetch()
    return None

@task
def fetch_feeds(callback=None):
    logging.warn("updating all feeds")
    feeds = Feed.objects.all()
    task_list = []
    for feed in feeds:
        s = fetch_feed.subtask([feed.id])
        task_list.append(s)
    fetch_all_tasks = TaskSet(tasks=task_list)
    fetch_all_tasks.apply_async()
    return None