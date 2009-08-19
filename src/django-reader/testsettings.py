import os
 
DEBUG = TEMPLATE_DEBUG = True
DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = '/tmp/feedreader.db'
INSTALLED_APPS = (
    'feedreader',
)
ROOT_URLCONF = ['feedreader.urls']
TEMPLATE_DIRS = os.path.join(os.path.dirname(__file__), 'templates')