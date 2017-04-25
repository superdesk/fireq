[ -z "${testing:-}" ] || (
{{>testing.sh}}
)

{{>superdesk/deploy.sh}}

service={{name}}-client
cat <<"EOF" > /etc/systemd/system/$service.service
[Unit]
Description={{name}}
Wants=network.target
After=network.target

[Service]
ExecStart=/bin/sh -c '. {{repo_env}}/bin/activate && exec grunt server --inline'
WorkingDirectory={{repo}}/client-core
Restart=always

[Install]
WantedBy=multi-user.target
EOF
systemctl enable $service
systemctl restart $service
