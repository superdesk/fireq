cat <<"EOF" > {{activate}}
{{>activate.sh}}
EOF

_activate

# Use latest honcho with --no-colour option
pip install -U honcho gunicorn

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

systemctl enable {{name}}
systemctl restart {{name}}

{{>add-nginx.sh}}

[ -z "${prepopulate-1}" ] || (
{{>prepopulate.sh}}
)

[ -z "${smtp-1}" ] || (
{{>add-smtp.sh}}
)
