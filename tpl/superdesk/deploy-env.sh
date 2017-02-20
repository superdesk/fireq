# don't change this file
# variables are loading in {{repo_env}}/bin/activate by the next order
# 1. /etc/{{name}}.sh
# 2. this file
# so rewrite you variables in /etc/{{name}}.sh
LANG=en_US.UTF-8
LANGUAGE=en_US:en
LC_ALL=en_US.UTF-8
PYTHONIOENCODING="utf-8"
PYTHONUNBUFFERED=1

HOST=${HOST:-localhost}
DB_HOST=${DB_HOST:-localhost}
DB_NAME=${DB_NAME:-'{{name}}'}
[ -n "${HOST_SSL:-}" ] && [ "$HOST" != 'localhost' ] && SSL='s' || SSL=''

# TODO: need to get rid this for proper SaaS
SUPERDESK_CLIENT_URL=${SUPERDESK_CLIENT_URL:-"http$SSL://$HOST"}

# To work properly inside and outside container, must be
# - "proxy_set_header Host <host>;" in nginx
# - the same "<host>" for next two settings
# TODO: try to fix at backend side, it should accept any host
SUPERDESK_URL=${SUPERDESK_URL:-"http$SSL://$HOST/api"}
CONTENTAPI_URL=${CONTENTAPI_URL:-"http$SSL://$HOST/contentapi"}


MONGO_URI=${MONGO_URI:-"mongodb://$DB_HOST/$DB_NAME"}
LEGAL_ARCHIVE_URI=${LEGAL_ARCHIVE_URI:-"mongodb://$DB_HOST/${DB_NAME}_la"}
ARCHIVED_URI=${ARCHIVED_URI:-"mongodb://$DB_HOST/${DB_NAME}_ar"}
ELASTICSEARCH_URL=${ELASTICSEARCH_URL:-"http://$DB_HOST:9200"}
ELASTICSEARCH_INDEX=${ELASTICSEARCH_INDEX:-"$DB_NAME"}

CONTENTAPI_ELASTICSEARCH_INDEX=${CONTENTAPI_ELASTICSEARCH_INDEX:-"${DB_NAME}_ca"}
# TODO: fix will be in 1.6 release, keep it for a while
CONTENTAPI_ELASTIC_INDEX=$CONTENTAPI_ELASTICSEARCH_INDEX
CONTENTAPI_MONGO_URI=${CONTENTAPI_MONGO_URI:-"mongodb://$DB_HOST/${CONTENTAPI_ELASTICSEARCH_INDEX}"}

REDIS_URL=${REDIS_URL:-redis://$DB_HOST:6379/1}

C_FORCE_ROOT=1
CELERYBEAT_SCHEDULE_FILENAME=${CELERYBEAT_SCHEDULE_FILENAME:-/tmp/celerybeatschedule}
CELERY_BROKER_URL=${CELERY_BROKER_URL:-$REDIS_URL}

MAIL_FROM=${MAIL_FROM-''}
MAIL_SERVER=${MAIL_SERVER-localhost}
MAIL_PASSWORD=${MAIL_PASSWORD-''}
MAIL_PORT=${MAIL_PORT-25}
MAIL_USERNAME=${MAIL_USERNAME-''}
MAIL_USE_SSL=${MAIL_USE_SSL-False}
MAIL_USE_TLS=${MAIL_USE_TLS-False}

AMAZON_ACCESS_KEY_ID=${AMAZON_ACCESS_KEY_ID:-}
AMAZON_SECRET_ACCESS_KEY=${AMAZON_SECRET_ACCESS_KEY:-}
AMAZON_CONTAINER_NAME=${AMAZON_CONTAINER_NAME:-}
AMAZON_S3_SUBFOLDER=${AMAZON_S3_SUBFOLDER:-$(hostname)}
AMAZON_REGION=${AMAZON_REGION:-'eu-west-1'}
AMAZON_SERVER=${AMAZON_SERVER:-amazonaws.com}
AMAZON_SERVE_DIRECT_LINKS=${AMAZON_SERVE_DIRECT_LINKS:-True}
AMAZON_S3_USE_HTTPS=${AMAZON_S3_USE_HTTPS:-False}
AMAZON_PROXY_SERVER=${AMAZON_PROXY_SERVER:-}
AMAZON_URL_GENERATOR=${AMAZON_URL_GENERATOR:-default}

IFRAMELY_KEY=${IFRAMELY_KEY:-}
SENTRY_DSN=${SENTRY_DSN:-}
NEW_RELIC_APP_NAME=${NEW_RELIC_APP_NAME:-}
NEW_RELIC_LICENSE_KEY=${NEW_RELIC_LICENSE_KEY:-}

if [ -n "${SUPERDESK_TESTING:-}" ]; then
    SUPERDESK_TESTING=True
    CELERY_ALWAYS_EAGER=True
    ELASTICSEARCH_BACKUPS_PATH=/tmp/es-backups
fi