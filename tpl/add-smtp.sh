mails={{logs}}/mail
mkdir -p $mails

smtp_py=/var/tmp/smtp.py
cat <<EOF > $smtp_py
{{>add-smtp.py}}
EOF

cat <<EOF >> /etc/nginx/conf.d/default.inc
location /mail {
    alias $mails/;
    default_type text/plain;
    autoindex on;
    autoindex_exact_size off;
}
EOF

service={{name}}-smtp
cat <<EOF > /etc/systemd/system/$service.service
[Unit]
Description=Dev SMTP server for {{name}}, it doesn't send real emails
Wants=network.target
After=network.target

[Service]
ExecStart=/bin/sh -c '. {{repo_env}}/bin/activate && exec python3 $smtp_py localhost 25 $mails'
WorkingDirectory={{repo}}
Restart=always

[Install]
WantedBy=multi-user.target
EOF
systemctl enable $service
systemctl restart $service

nginx -s reload
unset smtp_py mails
