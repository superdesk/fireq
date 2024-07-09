. {{activate}}
printenv | grep -v ELASTIC_PORT > {{repo}}/.env

cat <<"EOF" > /etc/systemd/system/{{name}}.service
[Unit]
Description={{name}}
Wants=network.target
After=network.target

[Service]
#ExecStart=/bin/sh -c '. {{activate}} && exec honcho start --no-colour'
ExecStart=/bin/sh -c '. {{repo}}/env/bin/activate && exec honcho start --no-colour'
WorkingDirectory={{repo}}/server
EnvironmentFile={{repo}}/.env
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
