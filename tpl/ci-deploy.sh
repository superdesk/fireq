lxc=${lxc:-"{{uid}}"}
db_host="{{db_host}}"
db_name="{{uid}}"

# env config
cat <<EOF | {{ssh}} $lxc "cat > {{config}}"
{{>deploy-config.sh}}
EOF

# run init
if [ -f tpl/init/{{uid}}.sh ]; then
    cfg={{uid}}
elif [ -f tpl/init/{{scope}}.sh ]; then
    cfg={{scope}}
else
    cfg=sd
fi
./fire r -s {{scope}} init/$cfg | {{ssh}} $lxc
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

[ -z "${pubapi-}" ] || (
{{>pubapi.sh}}
)
EOF2
