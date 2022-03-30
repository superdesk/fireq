. {{repo_env}}/bin/activate

set -a
LC_ALL=en_US.UTF-8
PYTHONUNBUFFERED=1
PATH=node_modules/.bin/:$PATH

[ ! -f {{config}} ] || . {{config}}

NEWSROOM_SETTINGS=settings.py
NEWSROOM_WEBSOCKET_URL="ws{{^is_pr}}s{{/is_pr}}://$HOST/ws"
NOTIFICATION_KEY="newsroom"
RECAPTCHA_PUBLIC_KEY="$RECAPTCHA_PUBLIC_KEY"
RECAPTCHA_PRIVATE_KEY="$RECAPTCHA_PRIVATE_KEY"
GOOGLE_MAPS_KEY="AIzaSyC14_pEv1mUFFDfUA2zNEzij3RFTcJk5wM"
SECRET_KEY=$DB_NAME
PUSH_KEY="newsroom"

# mongo
MONGO_URI="mongodb://$DB_HOST/$DB_NAME"
CONTENTAPI_MONGO_URI="mongodb://$DB_HOST/$DB_NAME"

# elastic
# 9200 is elastic 2.4, 9201 is elastic 7
_ELASTIC_PORT=${ELASTIC_PORT:-'9200'}

if [ -f {{fireq_json}} ] && [ `jq ".elastic?" {{fireq_json}}` -eq 7 ]; then
    _ELASTIC_PORT=9201
fi
ELASTICSEARCH_URL="http://$DB_HOST:$_ELASTIC_PORT"
CONTENTAPI_ELASTIC_INDEX=$DB_NAME
CONTENTAPI_ELASTICSEARCH_INDEX=$DB_NAME

# redis and celery
REDIS_URL=redis://localhost:6379/1
CELERY_BROKER_URL="$REDIS_URL"
CACHE_TYPE=RedisCache

{{#is_pr}}
MONGO_URI="mongodb://$DB_HOST/nr-master"
CONTENTAPI_ELASTIC_INDEX=nr-master
CONTENTAPI_ELASTICSEARCH_INDEX=nr-master
CONTENTAPI_MONGO_URI="mongodb://$DB_HOST/nr-master"
NEWS_API_ENABLED=true
{{/is_pr}}

# scope custom env for {{scope}}
{{env_string}}

set +a
