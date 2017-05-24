### deploy
cat <<"EOF" > {{activate}}
{{>activate.sh}}
EOF

_activate


[ -z "${prepopulate-1}" ] || (
{{>prepopulate.sh}}
)

[ -z "${grunt_build-1}" ] || (
cd {{repo_client}}
time grunt build --webpack-no-progress
)

[ -d {{logs}} ] || mkdir -p {{logs}}
systemctl disable rsyslog
systemctl stop rsyslog

# Use latest honcho with --no-colour option
pip install -U honcho gunicorn

gunicorn_opts='-t 300 -w 1 --access-logfile=- --access-logformat="%(m)s %(U)s status=%(s)s time=%(T)ss size=%(B)sb"{{#dev}} --reload{{/dev}}'
cat <<EOF > {{repo}}/server/Procfile
logs: journalctl -u {{name}}* -f >> {{logs}}/main.log
rest: gunicorn -b 0.0.0.0:5000 wsgi $gunicorn_opts
wamp: python3 -u ws.py
work: celery -A worker worker -c 1
beat: celery -A worker beat --pid=
{{#is_superdesk}}
capi: gunicorn -b 0.0.0.0:5400 content_api.wsgi $gunicorn_opts
{{/is_superdesk}}
EOF

service={{name}}
cat <<"EOF" > /etc/systemd/system/$service.service
[Unit]
Description={{name}}
Wants=network.target
After=network.target

[Service]
ExecStart=/bin/sh -c '. {{activate}} && exec honcho start --no-colour'
WorkingDirectory={{repo}}/server
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
systemctl enable $service
systemctl restart $service
unset service


{{>add-nginx.sh}}


[ -z "${smtp-1}" ] || (
{{>add-smtp.sh}}
)
