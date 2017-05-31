### deploy
cat <<"EOF" > {{activate}}
{{>activate.sh}}
EOF

_activate


[ -z "${prepopulate-1}" ] || (
{{>prepopulate.sh}}
)

{{^develop}}
[ -z "${grunt_build-1}" ] || (
cd {{repo_client}}
time grunt build --webpack-no-progress
)
{{/develop}}

[ -d {{logs}} ] || mkdir -p {{logs}}
systemctl disable rsyslog
systemctl stop rsyslog

cat <<"EOF" > /etc/logrotate.d/{{name}}
{{logs}}/*.log {
    rotate 7
    daily
    missingok
    copytruncate
    notifempty
    nocompress
    size 20M
}
EOF
logrotate /etc/logrotate.conf

# Use latest honcho with --no-colour option
pip install -U honcho gunicorn

gunicorn_opts='-t 300 -w 1 --access-logfile=- --access-logformat="%(m)s %(U)s status=%(s)s time=%(T)ss size=%(B)sb"'
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


cat <<"EOF" > /etc/systemd/system/{{name}}.service
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
{{#develop}}
{{>testing.sh}}

_skip_install inotify-tools || (
    apt-get update
    apt-get -y install inotify-tools
)
# server watcher
cat <<"EOF" > {{repo}}/watch-server
[ -d {{repo}}/server-core ] && cd {{repo}}/server-core || cd {{repo_server}}
while inotifywait -e modify -e create -e delete -r .; do
    systemctl restart {{name}}
done
EOF
cat <<EOF >> {{repo}}/server/Procfile
watch: sh {{repo}}/watch-server
EOF

# client watcher
cat <<"EOF" > {{repo}}/watch-client
. {{activate}}
cd {{repo_client}}
grunt build --webpack-devtool=cheap-eval-source-map --webpack-no-progress

[ -d {{repo}}/client-core ] && cd {{repo}}/client-core
while inotifywait -e modify -e create -e delete -r .; do
    systemctl restart {{name}}-client
done
EOF
service={{name}}-client
cat <<"EOF" > /etc/systemd/system/$service.service
[Unit]
Description={{name}} client watcher
Wants=network.target
After=network.target

[Service]
ExecStart=/bin/sh watch-client
WorkingDirectory={{repo}}
Restart=always

[Install]
WantedBy=multi-user.target
EOF
systemctl enable $service
systemctl restart $service
unset service

{{/develop}}
systemctl enable {{name}}
systemctl restart {{name}}

{{>add-nginx.sh}}


[ -z "${smtp-1}" ] || (
{{>add-smtp.sh}}
)
