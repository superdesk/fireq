lxc="{{uid}}--www";
./fire lxc-copy -cs -b {{lxc_build}} $lxc

# env config
(
[ ! -f etc/{{name}}.sh ] || cat etc/{{name}}.sh
[ ! -f etc/{{uid}}.sh ] || cat etc/{{uid}}.sh
cat <<EOF
{{>deploy-config.sh}}
EOF
) | {{ssh}} $lxc "cat > {{config}}"

# config.js
configjs={{repo_client}}/dist/config.*.js
[ ! -f etc/{{name}}.js ] || cat etc/{{name}}.js\
    | {{ssh}} $lxc "[ -f $configjs ] && cat > $configjs || cat /dev/null"
unset configjs

cat <<"EOF2" | {{ssh}} $lxc
cat <<"EOF" > /etc/nginx/conf.d/logs.inc
location /logs {
    return 302 {{logs_url}}/;
}
location /logs/ {
    return 302 {{logs_url}}/;
}
EOF

{{>header.sh}}

{{>add-dbs.sh}}

{{>deploy.sh}}

{{>prepopulate.sh}}
EOF2
./fire lxc-copy --no-snapshot -rc -b $lxc {{uid}}

# mount logs directory
mkdir -p {{host_logs}}
logs={{logs}}
cat <<EOF >> /var/lib/lxc/{{uid}}/config;
lxc.mount.entry = {{host_logs}} ${logs:1} none bind,create=dir
EOF
lxc-start -n {{uid}};
./fire2 nginx {{#host_ssl}}--ssl{{/host_ssl}} {{uid}} || true
