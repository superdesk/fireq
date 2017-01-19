lxc="{{name}}--www";
./fire lxc-copy -rcs -b {{lxc_build}} $lxc
cat << EOF | {{ssh}} $lxc
echo '
HOST={{name}}.test.superdesk.org
' > /etc/superdesk.sh
EOF
./fire2 run superdesk/deploy | {{ssh}} $lxc
./fire lxc-copy --no-snapshot -rc -b $lxc {{name}};
echo "lxc.mount.entry = {{logs}} var/log/superdesk none bind,create=dir" >>\
    /var/lib/lxc/{{name}}/config;
lxc-start -n {{name}};
./fire nginx || true
