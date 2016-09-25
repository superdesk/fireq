#!/bin/sh
set -x

[ -n "$services" ] && $root/bin/install_services.sh

repos=/opt/repos

DEBIAN_FRONTEND=noninteractive
apt-get -y install --no-install-recommends \
python3 python3-dev python3-venv python3-lxml \
build-essential libffi-dev git \
libtiff5-dev libjpeg8-dev zlib1g-dev \
libfreetype6-dev liblcms2-dev libwebp-dev \
curl libfontconfig nodejs npm daemon
apt-get -y clean

git clone --depth=1 https://github.com/superdesk/superdesk.git $repos/superdesk
git clone --depth=1 https://github.com/superdesk/superdesk-content-api.git $repos/superdesk-content-api
git clone --depth=1 https://github.com/superdesk/superdesk-core.git $repos/superdesk-core
git clone --depth=1 https://github.com/superdesk/superdesk-client-core.git $repos/superdesk-client-core

[ ! -f /usr/bin/node ] && ln -s /usr/bin/nodejs /usr/bin/node
npm -g install npm
npm -g install grunt-cli
locale-gen en_US.UTF-8

cd $repos/superdesk-client-core && npm install && grunt build

python3 -m venv $repos/.env/
. $repos/.env/bin/activate
pip install -U pip wheel
pip install -U -r $repos/superdesk-core/requirements.txt
pip install -U -e $repos/superdesk-core/
pip install -U -e $repos/superdesk-content-api/
pip install -U requests

if [ -n "$dev" ]; then
    cd $repos/superdesk/server
    python manage.py app:initialize_data
    python manage.py users:create -u admin -p superdesk -e 'admin@example.com' --admin

    cd $repos/superdesk-content-api
    python content_api_manage.py app:prepopulate

    cat $root/dev/nginx.conf  > /etc/nginx/conf.d/default.conf
    nginx -s reload

    cat $root/dev/systemd.service > /etc/systemd/system/superdesk.service
    systemctl enable superdesk
    systemctl start superdesk

    cat <<EOF > $repos/Procfile
rest: cd $repos/superdesk/server && gunicorn -c gunicorn_config.py wsgi
wamp: cd $repos/superdesk/server && python3 -u ws.py
work: cd $repos/superdesk/server && celery -A worker worker
beat: cd $repos/superdesk/server && celery -A worker beat --pid=
clnt: cd $repos/superdesk-client-core && grunt server
capi: cd $repos/superdesk-content-api && gunicorn -c gunicorn_config.py wsgi
EOF

fi
