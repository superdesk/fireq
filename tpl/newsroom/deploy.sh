cat <<"EOF" > {{activate}}
. {{repo_env}}/bin/activate

set -a
LC_ALL=en_US.UTF-8
PYTHONUNBUFFERED=1
PATH=node_modules/.bin/:$PATH

[ ! -f {{config}} ] || . {{config}}

NEWSROOM_SETTINGS=settings.py

CONTENTAPI_ELASTIC_INDEX=$DB_NAME
CONTENTAPI_ELASTICSEARCH_INDEX=$DB_NAME
CONTENTAPI_MONGO_URI=mongodb://data-sd/$DB_NAME
NEWSROOM_WEBSOCKET_URL="ws{{^is_pr}}s{{/is_pr}}://$HOST/ws"
ELASTICSEARCH_URL=http://data-sd:9200
REDIS_URL=redis://localhost:6379/1
CELERY_BROKER_URL="$REDIS_URL"
NOTIFICATION_KEY="newsroom"
RECAPTCHA_PUBLIC_KEY="$RECAPTCHA_PUBLIC_KEY"
RECAPTCHA_PRIVATE_KEY="$RECAPTCHA_PRIVATE_KEY"
GOOGLE_MAPS_KEY="AIzaSyC14_pEv1mUFFDfUA2zNEzij3RFTcJk5wM"

{{#is_pr}}
CONTENTAPI_ELASTIC_INDEX=nr-master
CONTENTAPI_ELASTICSEARCH_INDEX=nr-master
CONTENTAPI_MONGO_URI=mongodb://data-sd/nr-master
NEWS_API_ENABLED=true
{{/is_pr}}

set +a
EOF

_activate

cat <<EOF >> {{repo}}/settings.py
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
pip install -U honcho gunicorn

cat <<EOF > {{repo}}/Procfile
web: gunicorn -b 0.0.0.0:$PORT -w 3 app:app
websocket: python -m newsroom.websocket
worker: celery -A newsroom.worker.celery -Q "${SUPERDESK_CELERY_PREFIX}newsroom" worker
beat: celery -A newsroom.worker.celery beat --pid=
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

[ -z "${prepopulate-1}" ] || (
{{>prepopulate.sh}}
)

[ -z "${smtp-1}" ] || (
{{>add-smtp.sh}}
)
