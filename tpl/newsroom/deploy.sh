cat <<"EOF" > {{activate}}
. {{repo_env}}/bin/activate

set -a
LC_ALL=en_US.UTF-8
PYTHONUNBUFFERED=1
PATH=node_modules/.bin/:$PATH

[ ! -f {{config}} ] || . {{config}}

NEWSROOM_SETTINGS=settings.py

CONTENTAPI_ELASTIC_INDEX=sd-master_ca
CONTENTAPI_ELASTICSEARCH_INDEX=sd-master_ca
CONTENTAPI_MONGO_URI=mongodb://data-sd/sd-master_ca
CONTENTAPI_URL=https://sd-master.test.superdesk.org/contentapi
NEWSROOM_WEBSOCKET_URL="wss://$HOST/ws"
ELASTICSEARCH_URL=http://data-sd:9200
REDIS_URL=redis://localhost:6379/1
CELERY_BROKER_URL="$REDIS_URL"
NOTIFICATION_KEY="newsroom"

set +a
EOF

_activate

cat <<EOF > {{repo}}/settings.py
import os

env = os.environ.get

DEBUG=False

MAIL_SERVER = env('MAIL_SERVER', 'localhost')
MAIL_PORT = int(env('MAIL_PORT', 25))
MAIL_USE_TLS = env('MAIL_USE_TLS', False)
MAIL_USE_SSL = env('MAIL_USE_SSL', False)
MAIL_USERNAME = env('MAIL_USERNAME', '')
MAIL_PASSWORD = env('MAIL_PASSWORD', '')
EOF

# Use latest honcho with --no-colour option
pip install -U honcho

cat <<EOF > {{repo}}/Procfile
app: python app.py
websocket: python -m newsroom.websocket
logs: journalctl -u {{name}}* -f >> {{logs}}/main.log
EOF

cat <<"EOF" > /etc/systemd/system/{{name}}.service
[Unit]
Description={{name}}
Wants=network.target
After=network.target

[Service]
ExecStart=/bin/sh -c '. {{activate}} && exec honcho start --no-colour'
WorkingDirectory={{repo}}
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl enable {{name}}
systemctl restart {{name}}

{{>add-nginx.sh}}


[ -z "${smtp-1}" ] || (
{{>add-smtp.sh}}
)
