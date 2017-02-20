lxc="{{uid}}--www";

lxc-destroy -fn $lxc || true
lxc-copy -s -n {{lxc_build}} -N $lxc
./fire lxc-wait --start $lxc

# env config
cat <<EOF | {{ssh}} $lxc "cat > {{config}}"
{{>deploy-config.sh}}
EOF

# run init
if [ -f tpl/init/{{uid}}.sh ]; then
    cfg={{uid}}
else
    cfg={{scope}}
fi
./fire run init/$cfg | {{ssh}} $lxc
unset cfg

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
./fire nginx {{#host_ssl}}--ssl{{/host_ssl}} {{uid}} || true
