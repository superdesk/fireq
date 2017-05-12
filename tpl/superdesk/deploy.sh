### deploy
# write config if not exist
config={{config}}
[ -f $config ] || cat <<EOF > $config
{{>deploy-config.sh}}
EOF

# env.sh
envfile={{repo}}/env.sh
cat <<"EOF" > $envfile
{{>deploy-env.sh}}
EOF

# load env.sh and config in activation script
activate={{repo_env}}/bin/activate
grep "$envfile" $activate || cat <<EOF >> $activate
set -a
[ -f $config ] && . $config
. $envfile
set +a
EOF
unset envfile activate config
_activate


{{>add-nginx.sh}}


[ -z "${prepopulate-1}" ] || (
{{>prepopulate.sh}}
)


[ -d {{logs}} ] || mkdir -p {{logs}}
systemctl disable rsyslog
systemctl stop rsyslog

# Use latest honcho with --no-colour option
_activate
pip install -U honcho

gunicorn_opts='-t 300 -w 2 --access-logfile=- --access-logformat="%(m)s %(U)s status=%(s)s time=%(T)ss size=%(B)sb"{{#dev}} --reload{{/dev}}'
cat <<EOF > {{repo}}/server/Procfile
logs: journalctl -u {{name}}* -f >> {{logs}}/main.log
rest: gunicorn -b 0.0.0.0:5000 wsgi $gunicorn_opts
wamp: python3 -u ws.py
work: celery -A worker worker -c 2
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
ExecStart=/bin/sh -c '. {{repo_env}}/bin/activate && exec honcho start --no-colour'
WorkingDirectory={{repo}}/server
Restart=always

[Install]
WantedBy=multi-user.target
EOF
systemctl enable $service
systemctl restart $service
unset service


[ -z "${smtp-1}" ] || (
{{>add-smtp.sh}}
)
