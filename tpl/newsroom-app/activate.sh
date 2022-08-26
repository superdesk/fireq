. {{repo_env}}/bin/activate

set -a
LC_ALL=en_US.UTF-8
PYTHONUNBUFFERED=1
PATH=node_modules/.bin/:$PATH

[ ! -f {{config}} ] || . {{config}}

NEWSROOM_WEBSOCKET_URL="ws{{^is_pr}}s{{/is_pr}}://$HOST/ws"
NEWSAPI_URL="http$SSL://$HOST/newsapi/v1"
MGMTAPI_URL="http$SSL://$HOST/mgmtapi/v1"
NOTIFICATION_KEY="newsroom"
RECAPTCHA_PUBLIC_KEY="$RECAPTCHA_PUBLIC_KEY"
RECAPTCHA_PRIVATE_KEY="$RECAPTCHA_PRIVATE_KEY"
GOOGLE_MAPS_KEY="AIzaSyC14_pEv1mUFFDfUA2zNEzij3RFTcJk5wM"
SECRET_KEY=$DB_NAME
PUSH_KEY="newsroom"
WEBPACK_ASSETS_URL="/static/dist/"

# Management API vars
AUTH_SERVER_SHARED_SECRET=7fZOf0VI9T70vU5uNlKLrc5GlabxVgl6
# internal request is http not https
# see nginx.conf
AUTHLIB_INSECURE_TRANSPORT=1

# mongo
MONGO_URI="mongodb://$DB_HOST/$DB_NAME"
CONTENTAPI_MONGO_URI="mongodb://$DB_HOST/$DB_NAME"

# elastic
_ELASTIC_PORT=9201

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

# SDESK-6573: Enable running `app:rebuild_elastic_index` if `app:initialize_data` es mapping fails
REBUILD_ELASTIC_ON_INIT_DATA_ERROR=true

# scope custom env for {{scope}}
{{env_string}}

set +a
