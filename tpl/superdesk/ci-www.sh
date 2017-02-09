lxc="{{uid}}--www";

lxc-destroy -fn $lxc || true
lxc-copy -s -n {{lxc_build}} -N $lxc
./fire2 lxc-wait --start $lxc

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

lxc-stop -n $lxc
lxc-destroy -fn {{uid}} || true
lxc-copy -n $lxc -N {{uid}} -R

# mount logs directory
mkdir -p {{host_logs}}
logs={{logs}}
cat <<EOF >> /var/lib/lxc/{{uid}}/config;
lxc.mount.entry = {{host_logs}} ${logs:1} none bind,create=dir
EOF
lxc-start -n {{uid}};
./fire2 nginx {{#host_ssl}}--ssl{{/host_ssl}} {{uid}} || true
