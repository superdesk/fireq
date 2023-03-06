cat <<"EOF" > {{activate}}
{{>activate.sh}}
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
web: gunicorn -b 0.0.0.0:\$PORT -w 3 app:app
websocket: python -m newsroom.websocket
worker: celery -A newsroom.worker.celery -Q "\${SUPERDESK_CELERY_PREFIX}newsroom" worker
beat: celery -A newsroom.worker.celery beat --pid=
logs: journalctl -u "{{name}}*" -f >> {{logs}}/main.log
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

[ -z "${prepopulate-1}" ] || (
{{>prepopulate.sh}}
)


{{>add-nginx.sh}}

[ -z "${smtp-1}" ] || (
{{>add-smtp.sh}}
)
