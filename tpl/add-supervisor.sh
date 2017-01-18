### supervisor
if ! _skip_install supervisor; then
    apt-get -y install supervisor

    systemctl enable supervisor
    systemctl restart supervisor
    sleep 1
fi

[ -d {{logs}} ] || mkdir {{logs}}
cat << "EOF" > /etc/supervisor/conf.d/{{name}}.conf
{{>supervisor.conf}}
EOF
supervisorctl update
supervisorctl restart all
