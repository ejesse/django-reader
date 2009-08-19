import os
 
DEBUG = TEMPLATE_DEBUG = True
DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = '/tmp/reader.db'
INSTALLED_APPS = (
    'reader',
)
ROOT_URLCONF = ['reader.urls']
TEMPLATE_DIRS = os.path.join(os.path.dirname(__file__), 'templates')