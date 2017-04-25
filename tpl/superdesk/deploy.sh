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


{{>deploy-dist.sh}}


{{>add-nginx.sh}}


[ -z "${prepopulate-1}" ] || (
{{>prepopulate.sh}}
)


[ -d {{logs}} ] || mkdir -p {{logs}}
systemctl disable rsyslog
systemctl stop rsyslog

service={{name}}-logs
cat <<"EOF" > /etc/systemd/system/$service.service
[Unit]
Description=Redirect superdesk logs to file
After=systemd-journald.service
Requires=systemd-journald.service

[Service]
ExecStart=/bin/sh -c "journalctl -u superdesk* -f > {{logs}}/main.log"
Restart=always

[Install]
WantedBy=multi-user.target
EOF
systemctl enable $service
systemctl restart $service

# Use latest honcho with --no-colour option
_activate
pip install -U honcho

cat <<"EOF" > {{repo}}/server/Procfile
rest: gunicorn -b 0.0.0.0:5000 -t 300 -w 2 wsgi{{#dev}} --reload{{/dev}}
wamp: python3 -u ws.py
work: celery -A worker worker -c 2
beat: celery -A worker beat --pid=
{{#is_superdesk}}
capi: gunicorn -b 0.0.0.0:5400 -t 300 -w 2 content_api.wsgi{{#dev}} --reload{{/dev}}
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
