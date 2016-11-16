cat <<EOF
LANG=en_US.UTF-8
LANGUAGE=en_US:en
LC_ALL=en_US.UTF-8
PYTHONIOENCODING="utf-8"
PYTHONUNBUFFERED=1

MONGO_URI=${MONGO_URI:-"mongodb://127.0.0.1/${name}"}
PUBLICAPI_MONGO_URI=${PUBLICAPI_MONGO_URI:-"mongodb://127.0.0.1/${name}_pa"}
LEGAL_ARCHIVE_URI=${LEGAL_ARCHIVE_URI:-"mongodb://127.0.0.1/${name}_la"}
ARCHIVED_URI=${ARCHIVED_URI:-"mongodb://127.0.0.1/${name}_ar"}
ELASTICSEARCH_URL=${ELASTICSEARCH_URL:-"http://127.0.0.1:9200"}
ELASTICSEARCH_INDEX=${name}

C_FORCE_ROOT=1
CELERYBEAT_SCHEDULE_FILENAME=${CELERYBEAT_SCHEDULE_FILENAME:-/tmp/celerybeatschedule}
CELERY_BROKER_URL=${CELERY_BROKER_URL:-redis://127.0.0.1:6379/1}
REDIS_URL=${REDIS_URL:-redis://127.0.0.1:6379/1}

MAIL_SERVER=${MAIL_SERVER-localhost}
MAIL_PASSWORD=${MAIL_PASSWORD-''}
MAIL_PORT=${MAIL_PORT-25}
MAIL_USERNAME=${MAIL_USERNAME-''}
MAIL_USE_SSL=${MAIL_USE_SSL-False}
MAIL_USE_TLS=${MAIL_USE_TLS-False}

# TODO: need to get rid this for proper SaaS
SUPERDESK_CLIENT_URL=${SUPERDESK_CLIENT_URL:-"http://$host"}

# To work properly inside and outside container, must be
# - "proxy_set_header Host {{host}};" in nginx
# - the same "{{host}}" for next two settings
# TODO: try to fix at backend side, it should accept any host
SUPERDESK_URL=${SUPERDESK_URL:-"http://$host/api"}
PUBLICAPI_URL=${PUBLICAPI_URL:-"http://$host/pubapi"}

$envfile_append
EOF
