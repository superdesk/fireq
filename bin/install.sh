#!/bin/sh
set -xe

[ -n "$services" ] && $root/bin/install_services.sh

repos=/opt

DEBIAN_FRONTEND=noninteractive
apt-get -y install --no-install-recommends \
python3 python3-dev python3-venv python3-lxml \
build-essential libffi-dev git \
libtiff5-dev libjpeg8-dev zlib1g-dev \
libfreetype6-dev liblcms2-dev libwebp-dev \
curl libfontconfig libssl-dev
apt-get -y clean

locale-gen en_US.UTF-8

[ -d $repos/superdesk ] || git clone --depth=1 https://github.com/superdesk/superdesk.git $repos/superdesk
[ -d $repos/superdesk-content-api ] || git clone --depth=1 https://github.com/superdesk/superdesk-content-api.git $repos/superdesk-content-api

cat <<EOF > $repos/superdesk/env-file
LANG=en_US.UTF-8
LANGUAGE=en_US:en
LC_ALL=en_US.UTF-8
PYTHONIOENCODING="utf-8"
PYTHONUNBUFFERED=1
C_FORCE_ROOT="False"
CELERYBEAT_SCHEDULE_FILENAME=/tmp/celerybeatschedule
SUPERDESK_URL=http://localhost/api
SUPERDESK_WS_URL=ws://localhost/ws
PUBLICAPI_URL=http://localhost/pubapi
SUPERDESK_CLIENT_URL=http://localhost
MONGO_URI=mongodb://127.0.0.1/superdesk
PUBLICAPI_MONGO_URI=mongodb://127.0.0.1/superdesk_pa
LEGAL_ARCHIVE_URI=mongodb://127.0.0.1/superdesk_la
ARCHIVED_URI=mongodb://127.0.0.1/superdesk_ar
ELASTICSEARCH_URL=http://127.0.0.1:9200
ELASTICSEARCH_INDEX=superdesk
CELERY_BROKER_URL=redis://127.0.0.1:6379/1
REDIS_URL=redis://127.0.0.1:6379/1
LOG_SERVER_ADDRESS=127.0.0.1
LOG_SERVER_PORT=5555
AMAZON_ACCESS_KEY_ID=
AMAZON_CONTAINER_NAME=
AMAZON_REGION=
AMAZON_SECRET_ACCESS_KEY=
AMAZON_SERVE_DIRECT_LINKS=True
AMAZON_S3_USE_HTTPS=False
AMAZON_SERVER=
AMAZON_PROXY_SERVER=
AMAZON_URL_GENERATOR=default
REUTERS_USERNAME=
REUTERS_PASSWORD=
MAIL_SERVER=127.0.0.1
MAIL_PORT=25
MAIL_USE_TLS=false
MAIL_USE_SSL=false
MAIL_USERNAME=__EMPTY__
MAIL_PASSWORD=__EMPTY__
SENTRY_DSN=
VIEW_DATE_FORMAT=
VIEW_TIME_FORMAT=
DEFAULT_SOURCE_VALUE_FOR_MANUAL_ARTICLES=
REUTERS_USERNAME=
REUTERS_PASSWORD=
EOF

# node & npm
curl -sL https://deb.nodesource.com/setup_6.x | sudo -E bash -
apt-get install -y nodejs
apt-get -y clean
[ ! -f /usr/bin/node ] && ln -s /usr/bin/nodejs /usr/bin/node
npm install -g grunt-cli

cd $repos/superdesk/client
npm install
grunt build

venv() {
    path=$1
    python3 -m venv $path
    echo "export \$(cat $repos/superdesk/env-file)" >> $path/bin/activate
    . $path/bin/activate
    pip install -U pip wheel
}
venv_main=$repos/superdesk/env
venv $venv_main
pip install -U -r $repos/superdesk/server/requirements.txt

venv_capi=$repos/superdesk-content-api/env
venv $venv_capi
pip install -U -r $repos/superdesk-content-api/requirements.txt

if [ -n "$dev" ]; then
    cp $root/dev/nginx.conf  /etc/nginx/conf.d/default.conf
    cp $root/dev/nginx-params.conf  /etc/nginx/conf.d/params.conf
    nginx -s reload

    . $venv_main/bin/activate
    cd $repos/superdesk/server
    python manage.py app:initialize_data
    python manage.py users:create -u admin -p admin -e 'admin@example.com' --admin

    . $venv_capi/bin/activate
    cd $repos/superdesk-content-api
    set +e
    python content_api_manage.py app:prepopulate
    set -e
fi
