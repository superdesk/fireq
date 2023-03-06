### deploy
cat <<"EOF" > {{activate}}
{{>activate.sh}}
EOF
{{#testing}}
cat <<"EOF" >> {{config}}
SUPERDESK_TESTING=1
EOF
{{/testing}}
_activate

[ -z "${prepopulate-1}" ] || (
{{>prepopulate.sh}}
)

{{^develop}}
[ -z "${grunt_build-1}" ] || (
export NODE_OPTIONS=--max_old_space_size=4096
cd {{repo_client}}
time (npm run build || npx grunt build --webpack-no-progress)
)
{{/develop}}

# Use latest honcho with --no-colour option
pip install -U honcho gunicorn

gunicorn_opts='-t 300 -w 1 --access-logfile=- --access-logformat="%(m)s %(U)s status=%(s)s time=%(T)ss size=%(B)sb"'

# keep repo Procfile for superdesk
{{#is_superdesk}}
cat <<EOF >> {{repo}}/server/Procfile
logs: journalctl -u "{{name}}*" -f >> {{logs}}/main.log
EOF
{{/is_superdesk}}

{{^is_superdesk}}
cat <<EOF > {{repo}}/server/Procfile
{{>Procfile}}
EOF
{{/is_superdesk}}

# If SAMS is enabled in fireq.json, add SAMS WSGI to the Procfile
if [ `_get_json_value sams` == "true" ]; then
    cat <<EOF >> {{repo}}/server/Procfile
sams: gunicorn -b localhost:5700 --chdir {{repo}}/server/sams sams.apps.api.wsgi $gunicorn_opts
EOF
fi

{{>service-superdesk.sh}}

# if grammalecte is enabled in fireq.json, add & run correspondent service
if [ -f {{fireq_json}} ] && [ `jq ".grammalecte?" {{fireq_json}}` == "true" ]; then
{{>service-grammalecte.sh}}
fi

# if videoserver is enabled in fireq.json, add & run correspondent service
if [ -f {{fireq_json}} ] && [ `jq ".videoserver?" {{fireq_json}}` == "true" ]; then
{{>service-videoserver.sh}}
fi

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
time node --max-old-space-size=4096  `which grunt` build --webpack-no-progress

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
