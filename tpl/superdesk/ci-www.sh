lxc="{{uid}}--www";
./fire lxc-copy -cs -b {{lxc_build}} $lxc
cat <<"EOF2" | {{ssh}} $lxc
{{>header.sh}}

{{>add-dbs.sh}}

{{>deploy.sh}}

{{>prepopulate.sh}}
EOF2
./fire lxc-copy --no-snapshot -rc -b $lxc {{uid}}

# mount logs directory
mkdir -p {{host_logs.www}}
logs={{logs}}
cat <<EOF >> /var/lib/lxc/{{uid}}/config;
lxc.mount.entry = {{host_logs.www}} ${logs:1} none bind,create=dir
EOF
lxc-start -n {{uid}};
./fire nginx || true
