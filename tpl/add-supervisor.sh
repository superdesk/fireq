# supervisor
if ! _skip_install supervisor; then
    apt-get -y install supervisor
fi

[ -d {{logs}} ] || mkdir -p {{logs}}
cat <<"EOF" > /etc/supervisor/conf.d/{{name}}.conf
{{>supervisor.conf}}
EOF
systemctl enable supervisor
systemctl restart supervisor
sleep 1
