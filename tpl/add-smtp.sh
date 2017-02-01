mails={{logs}}/mail
mkdir -p $mails

smtp_py=/var/tmp/smtp.py
cat <<EOF > $smtp_py
{{>add-smtp.py}}
EOF

cat <<EOF > /etc/nginx/conf.d/mail.inc
location /mail {
    return 302 \$scheme://\$host/mail/;
}
location /mail/ {
    alias $mails/;
    default_type text/plain;
    autoindex on;
    autoindex_exact_size off;
}
EOF

cat <<EOF >> /etc/supervisor/conf.d/mail.conf
[program:mail]
command=python3 $smtp_py localhost 25 $mails
autostart=true
autorestart=true
stdout_logfile={{logs}}/mail.log
redirect_stderr=true
EOF

supervisorctl update
nginx -s reload
unset smtp_py mails
