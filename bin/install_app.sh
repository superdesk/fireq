#!/bin/sh
set -x

DEBIAN_FRONTEND=noninteractive
apt-get -y install --no-install-recommends \
python3 python3-dev python3-venv python3-lxml \
build-essential libffi-dev git \
libtiff5-dev libjpeg8-dev zlib1g-dev \
libfreetype6-dev liblcms2-dev libwebp-dev \
curl libfontconfig nodejs npm daemon
apt-get -y clean

git clone --depth=1 https://github.com/superdesk/superdesk.git /opt/superdesk
git clone --depth=1 https://github.com/superdesk/superdesk-content-api.git /opt/superdesk-content-api
git clone --depth=1 https://github.com/superdesk/superdesk-core.git /opt/superdesk-core
git clone --depth=1 https://github.com/superdesk/superdesk-client-core.git /opt/superdesk-client-core

[ ! -f /usr/bin/node ] && ln -s /usr/bin/nodejs /usr/bin/node
# npm -g install npm
# npm -g install grunt-cli
# locale-gen en_US.UTF-8

# cd /opt/superdesk-client-core && npm install && grunt build

python3 -m venv /opt/superdesk-env/
source /opt/superdesk-env/bin/activate
pip install -U pip wheel
# pip install -U -r /opt/superdesk-core/requirements.txt
# pip install -U -e /opt/superdesk-core/
pip install -U -e /opt/superdesk-content-api/
pip install -U requests

if [ -n "$dev" ]; then
    # cd /opt/superdesk/server
    # python manage.py app:initialize_data
    # python manage.py users:create -u admin -p superdesk -e 'admin@example.com' --admin

    # cd /opt/superdesk-content-api
    # python content_api_manage.py app:prepopulate

    # Files
    cat << EOF > /etc/nginx/conf.d/default.conf
server {
    listen 80 default;

    location /ws {
        proxy_pass http://localhost:5100;
        proxy_http_version 1.1;
        proxy_buffering off;
        proxy_read_timeout 3600;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
    }

    location /api {
        proxy_pass http://localhost:5000;
        sub_filter_types application/json;
        sub_filter_once off;
        sub_filter 'http://localhost' 'http://$host';
    }

    location /pubapi {
        proxy_pass http://localhost:5050;
    }

    location / {
        proxy_pass http://localhost:9000;

        sub_filter_once off;
        sub_filter_types application/javascript;
        sub_filter 'http://localhost:9000' 'http://$host:9000';
        sub_filter 'http://localhost:5000' 'http://$host';
        sub_filter 'ws://0.0.0.0:5100' 'ws://$host/ws';
    }
}
EOF
    nginx -s reload

    cat << EOF > /opt/Procfile
rest: cd /opt/superdesk/server && gunicorn -c gunicorn_config.py wsgi
wamp: cd /opt/superdesk/server && python3 -u ws.py
work: cd /opt/superdesk/server && celery -A worker worker
beat: cd /opt/superdesk/server && celery -A worker beat --pid=
clnt: cd /opt/superdesk-client-core && grunt server
capi: cd /opt/superdesk-content-api && gunicorn -c gunicorn_config.py wsgi
EOF

    cat << EOF > /etc/systemd/system/superdesk.service
[Unit]
Description=Superdesk
After=elasticsearch.service mongod.service redis-server.service

[Service]
Environment=C_FORCE_ROOT=1
ExecStart=/usr/bin/daemon --name superdesk --pidfiles /var/run /bin/bash -c "source /opt/superdesk-env/bin/activate && honcho -d /opt start"
Type=notify

[Install]
WantedBy=multi-user.target
EOF
    systemctl enable superdesk
    systemctl start superdesk
fi
