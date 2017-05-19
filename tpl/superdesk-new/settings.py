import inspect
import os

env = os.environ.get


def f(s):
    frame = inspect.stack()[1][0]
    return s.format(**frame.f_locals)


DB_HOST = env('DB_HOST', 'localhost')
DB_NAME = env('DB_NAME', '{{name}}')

ELASTICSEARCH_INDEX = DB_NAME
ELASTICSEARCH_URL = f('http://{DB_HOST}:9200')
MONGO_URI = f('mongodb://{DB_HOST}/{DB_NAME}')
LEGAL_ARCHIVE_URI = f('mongodb://{DB_HOST}/{DB_NAME}_la')
ARCHIVED_URI = f('mongodb://{DB_HOST}/{DB_NAME}_ar')

DB_NAME_CA = f('{DB_NAME}_ca')
CONTENTAPI_ELASTICSEARCH_INDEX = DB_NAME_CA
CONTENTAPI_MONGO_URI = f('mongodb://{DB_HOST}/{DB_NAME_CA}')

REDIS_URL = env('REDIS_URL', 'redis://localhost:6379/1')
CELERY_BROKER_URL = REDIS_URL
CELERY_BEAT_SCHEDULE_FILENAME = '/tmp/celerybeatschedule'

CLIENT_URL = env('CLIENT_URL', 'http://localhost')
SERVER_DOMAIN = 'localhost'
SERVER_NAME = None
URL_PREFIX = None

MEDIA_PREFIX = f('{CLIENT_URL}/media')

SUPERDESK_TESTING = env('SUPERDESK_TESTING', False)
if SUPERDESK_TESTING:
    SUPERDESK_TESTING=True
    CELERY_ALWAYS_EAGER=True
    ELASTICSEARCH_BACKUPS_PATH='/var/tmp/elasticsearch'
    LEGAL_ARCHIVE=True
