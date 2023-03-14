# you could write variables to {{config}}
. {{repo_env}}/bin/activate

set -a
LC_ALL=en_US.UTF-8
PYTHONUNBUFFERED=1
PATH={{repo_client}}/node_modules/.bin/:$PATH

[ ! -f {{config}} ] || . {{config}}

HOST=${HOST:-'localhost'}
HOST_SSL=${HOST_SSL:-}
DB_HOST=${DB_HOST:-'localhost'}
DB_NAME=${DB_NAME:-'{{name}}'}

[ -n "${HOST_SSL:-}" ] && SSL='s' || SSL=''
# To work properly inside and outside container, must be
# - "proxy_set_header Host <host>;" in nginx
# - the same "<host>" for next two settings
# TODO: try to fix at backend side, it should accept any host
SUPERDESK_URL="http$SSL://$HOST/api"
CONTENTAPI_URL="http$SSL://$HOST/contentapi"
SUPERDESK_WS_URL="ws$SSL://$HOST/ws"
SUPERDESK_CLIENT_URL="http$SSL://$HOST"
PRODAPI_URL="http$SSL://$HOST"
PRODAPI_URL_PREFIX=prodapi
AUTH_SERVER_SHARED_SECRET=7fZOf0VI9T70vU5uNlKLrc5GlabxVgl6
# internal request is http not https
# see nginx.conf
AUTHLIB_INSECURE_TRANSPORT=1

MONGO_URI="mongodb://$DB_HOST/$DB_NAME"
LEGAL_ARCHIVE_DBNAME="${DB_NAME}_la"
LEGAL_ARCHIVE_URI="mongodb://$DB_HOST/${LEGAL_ARCHIVE_DBNAME}"
ARCHIVED_DBNAME="${DB_NAME}_ar"
ARCHIVED_URI="mongodb://$DB_HOST/${ARCHIVED_DBNAME}"

# use elastic based on superdesk-core config
_ELASTIC_PORT=${ELASTIC_PORT:-'9201'}
{{^db_local}}
[ -f {{fireq_json}} ] && [ `jq ".elastic?" {{fireq_json}}` -eq 2 ] && _ELASTIC_PORT=9200
{{/db_local}}
ELASTICSEARCH_URL="http://$DB_HOST:$_ELASTIC_PORT"
ELASTICSEARCH_INDEX="$DB_NAME"

PREFERRED_URL_SCHEME="https"

# analytics
STATISTICS_ELASTIC_URL="$ELASTICSEARCH_URL"
STATISTICS_ELASTIC_INDEX="${DB_NAME}_statistics"

CONTENTAPI_ELASTICSEARCH_INDEX="${DB_NAME}_ca"
# TODO: fix will be in 1.6 release, keep it for a while
CONTENTAPI_ELASTIC_INDEX=$CONTENTAPI_ELASTICSEARCH_INDEX
CONTENTAPI_MONGO_DBNAME=$CONTENTAPI_ELASTICSEARCH_INDEX
CONTENTAPI_MONGO_URI="mongodb://$DB_HOST/${CONTENTAPI_ELASTICSEARCH_INDEX}"

REDIS_URL=${REDIS_URL:-redis://$DB_HOST:6379/1}

C_FORCE_ROOT=1
CELERYBEAT_SCHEDULE_FILENAME=${CELERYBEAT_SCHEDULE_FILENAME:-/tmp/celerybeatschedule}
CELERY_BROKER_URL=${CELERY_BROKER_URL:-$REDIS_URL}

if [ -n "${AMAZON_CONTAINER_NAME:+isset}" ]; then
    AMAZON_S3_SUBFOLDER=${AMAZON_S3_SUBFOLDER:-'{{db_name}}'}
    MEDIA_PREFIX=${MEDIA_PREFIX:-"http$SSL://$HOST/api/upload-raw"}

    # TODO: remove after full adoption of MEDIA_PREFIX
    AMAZON_SERVE_DIRECT_LINKS=${AMAZON_SERVE_DIRECT_LINKS:-True}
    AMAZON_S3_USE_HTTPS=${AMAZON_S3_USE_HTTPS:-True}
fi

if [ -n "${SUPERDESK_TESTING:-}" ]; then
    SUPERDESK_TESTING=True
    CELERY_ALWAYS_EAGER=True
    ELASTICSEARCH_BACKUPS_PATH=/var/tmp/elasticsearch
    LEGAL_ARCHIVE=True
fi

{{#is_superdesk}}
week_minutes="10080"
CONTENT_EXPIRY_MINUTES="$week_minutes"
PUBLISHED_CONTENT_EXPIRY_MINUTES="$week_minutes"
AUDIT_EXPIRY_MINUTES="$week_minutes"
PUBLISH_QUEUE_EXPIRY_MINUTES="$week_minutes"
ARCHIVED_EXPIRY_MINUTES="10080"
MAX_EXPIRY_QUERY_LIMIT="500"
WEB_TIMEOUT=300
WEB_CONCURRENCY=1
CELERY_WORKER_CONCURRENCY=1
{{/is_superdesk}}

{{^is_superdesk}}
### Liveblog custom
S3_THEMES_PREFIX=${S3_THEMES_PREFIX:-"/{{db_name}}/"}
EMBEDLY_KEY=${EMBEDLY_KEY:-}
{{/is_superdesk}}

SAMS_HOST="localhost"
SAMS_PORT="5700"
SAMS_URL="http://localhost:5700"
SAMS_MONGO_DBNAME="${DB_NAME}_sams"
SAMS_MONGO_URI="mongodb://$DB_HOST/$SAMS_MONGO_DBNAME"
SAMS_ELASTICSEARCH_URL="$ELASTICSEARCH_URL"
SAMS_ELASTICSEARCH_INDEX="$SAMS_MONGO_DBNAME"
STORAGE_DESTINATION_1="MongoGridFS,Default,$SAMS_MONGO_URI"

MAIL_FROM=admin@test.superdesk.org
MAIL_SERVER=localhost
MAIL_PORT=25
MAIL_USERNAME=__EMPTY__
MAIL_PASSWORD=__EMPTY__

if [ -f {{fireq_json}} ] && [ `jq ".videoserver?" {{fireq_json}}` == "true" ]; then
  VIDEO_SERVER_ENABLED=True
fi

# SDESK-6573: Enable running `app:rebuild_elastic_index` if `app:initialize_data` es mapping fails
REBUILD_ELASTIC_ON_INIT_DATA_ERROR=true

# scope custom env for {{scope}}
{{env_string}}

set +a
