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

[ -z "${db_clean:-}" ] || (
./fire lxc-db -cb - $lxc
)
cat <<"EOF2" | {{ssh}} $lxc
{{>header.sh}}

cat <<"EOF" > /etc/nginx/conf.d/logs.inc
location /logs {
    return 302 {{logs_url}}/;
}
location /logs/ {
    return 302 {{logs_url}}/;
}
EOF

{{>add-dbs.sh}}

{{>deploy.sh}}

# it's just simpler rebuild client with env vars than
# trying to replace with nginx or fill config.js correctly
_activate
cd {{repo_client}}
time grunt build

[ -z "${pubapi-}" ] || (
{{>pubapi.sh}}
)
EOF2
