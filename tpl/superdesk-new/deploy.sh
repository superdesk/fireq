### deploy
cd {{repo}}
cat <<"EOF" > activate
# use virtualenv
. {{repo_env}}/bin/activate

set -a
PATH=./node_modules/.bin/:$PATH
LANG=en_US.UTF-8
LANGUAGE=en_US:en
LC_ALL=en_US.UTF-8
PYTHONIOENCODING="utf-8"
PYTHONUNBUFFERED=1
C_FORCE_ROOT=1

# put custom settings below

# should be in the end
set +a
EOF
cat <<"EOF" > settings.py
{{>settings.py}}
EOF
cat <<"EOF" > manage.py
{{>manage.py}}
EOF
chmod +x manage.py


[ -z "${prepopulate-1}" ] || (
{{>prepopulate.sh}}
)


[ -d {{logs}} ] || mkdir -p {{logs}}
systemctl disable rsyslog
systemctl stop rsyslog

# Use latest honcho with --no-colour option
_activate
pip install -U honcho gunicorn

gunicorn_opts='-t 300 -w 2 --access-logfile=- --access-logformat="%(m)s %(U)s status=%(s)s time=%(T)ss size=%(B)sb"{{#dev}} --reload{{/dev}}'
cat <<EOF > {{repo}}/Procfile
logs: journalctl -u {{name}}* -f >> {{logs}}/main.log
rest: gunicorn -b 0.0.0.0:5000 manage $gunicorn_opts
wamp: python manage.py ws
work: celery -A manage worker -c 2
beat: celery -A manage beat --pid=
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
ExecStart=/bin/sh -c '. {{repo}}/activate; exec honcho start --no-colour'
WorkingDirectory={{repo}}
Restart=always
RestartSec=10s

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
