#!/usr/bin/env python
# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014, 2015 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import os
from pathlib import Path

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse


def env(variable, fallback_value=None):
    env_value = os.environ.get(variable, '')
    if len(env_value) == 0:
        return fallback_value
    else:
        if env_value == "__EMPTY__":
            return ''
        else:
            return env_value


ABS_PATH = str(Path(__file__).resolve().parent)

init_data = Path(ABS_PATH) / 'data'
if init_data.exists():
    INIT_DATA_PATH = init_data

RENDITIONS = {
    'picture': {
        'thumbnail': {'width': 220, 'height': 120},
        'viewImage': {'width': 640, 'height': 640},
        'baseImage': {'width': 1400, 'height': 1400},
    },
    'avatar': {
        'thumbnail': {'width': 60, 'height': 60},
        'viewImage': {'width': 200, 'height': 200},
    }
}

WS_HOST = env('WSHOST', '0.0.0.0')
WS_PORT = env('WSPORT', '5100')

LOG_CONFIG_FILE = env('LOG_CONFIG_FILE', 'logging_config.yml')
SECRET_KEY = env('SECRET_KEY', '')
NO_TAKES = True

db_host = env('DB_HOST', '{{ db_host }}')
db_name = env('DB_NAME', '{{ db_name }}')

server_url = urlparse(env('SUPERDESK_URL', '{{ host_url}}/api'))
URL_PROTOCOL = server_url.scheme or None
SERVER_NAME = server_url.netloc or None
SERVER_DOMAIN = server_url.netloc or 'localhost'
URL_PREFIX = server_url.path.lstrip('/') or ''
if SERVER_NAME.endswith(':80'):
    SERVER_NAME = SERVER_NAME[:-3]

CELERYBEAT_SCHEDULE_FILENAME = env('CELERYBEAT_SCHEDULE_FILENAME', '/tmp/celerybeatschedule')
SUPERDESK_WS_URL = env('SUPERDESK_WS_URL', '{{ host_ws }}/ws')
CONTENTAPI_URL = env('CONTENTAPI_URL', '{{ host_url }}/contentapi')
SUPERDESK_CLIENT_URL = env('SUPERDESK_CLIENT_URL', '{{ host_url }}')
MONGO_URI = env('MONGO_URI', 'mongodb://{}/{}'.format(db_host, db_name))
CONTENTAPI_MONGO_URI = env('CONTENTAPI_MONGO_URI', 'mongodb://{}/{}_ca'.format(db_host, db_name))
LEGAL_ARCHIVE_URI = env('LEGAL_ARCHIVE_URI', 'mongodb://{}/{}_la'.format(db_host, db_name))
ARCHIVED_URI = env('ARCHIVED_URI', 'mongodb://{}/{}_ar'.format(db_host, db_name))
ELASTICSEARCH_URL = env('ELASTICSEARCH_URL', 'http://{}:9200'.format(db_host))
ELASTICSEARCH_INDEX = env('ELASTICSEARCH_INDEX', db_name)
CONTENTAPI_ELASTICSEARCH_INDEX = env('CONTENTAPI_ELASTICSEARCH_INDEX', '{}_ca'.format(db_name))
REDIS_URL = env('REDIS_URL', 'redis://{}:6379/1'.format(db_host))
CELERY_BROKER_URL = env('CELERY_BROKER_URL', REDIS_URL)
BROKER_URL = env('CELERY_BROKER_URL', REDIS_URL)
AMAZON_ACCESS_KEY_ID = env('AMAZON_ACCESS_KEY_ID', '')
AMAZON_SECRET_ACCESS_KEY = env('AMAZON_SECRET_ACCESS_KEY', '')
AMAZON_CONTAINER_NAME = env('AMAZON_CONTAINER_NAME', '')
AMAZON_REGION = env('AMAZON_REGION', 'eu-west-1')
AMAZON_S3_SUBFOLDER = env('AMAZON_S3_SUBFOLDER', '')
AMAZON_SERVE_DIRECT_LINKS = env('AMAZON_SERVE_DIRECT_LINKS', True)
AMAZON_S3_USE_HTTPS = env('AMAZON_S3_USE_HTTPS', False)
AMAZON_SERVER = env('AMAZON_SERVER', 'amazonaws.com')
AMAZON_PROXY_SERVER = env('AMAZON_PROXY_SERVER', '')
AMAZON_URL_GENERATOR = env('AMAZON_URL_GENERATOR', 'default')
MAIL_SERVER = env('MAIL_SERVER', 'localhost')
MAIL_PORT = env('MAIL_PORT', 25)
MAIL_USE_TLS = env('MAIL_USE_TLS', False)
MAIL_USE_SSL = env('MAIL_USE_SSL', False)
MAIL_USERNAME = env('MAIL_USERNAME', '')
MAIL_PASSWORD = env('MAIL_PASSWORD', '')
MAIL_FROM = env('MAIL_FROM', '')
SENTRY_DSN = env('SENTRY_DSN', '')
IFRAMELY_KEY = env('IFRAMELY_KEY', '')
NEW_RELIC_APP_NAME = env('NEW_RELIC_APP_NAME', '')
NEW_RELIC_LICENSE_KEY = env('NEW_RELIC_LICENSE_KEY', '')
