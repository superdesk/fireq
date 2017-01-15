### supervisor
add() {
    _skip_install supervisor && return 0
    apt-get -y install supervisor

    systemctl enable supervisor
    systemctl restart supervisor
    sleep 1
}
add

[ -d {{logs}} ] || mkdir {{logs}}
cat << "EOF" > /etc/supervisor/conf.d/{{name}}.conf
{{>supervisor.conf}}
EOF
supervisorctl update
