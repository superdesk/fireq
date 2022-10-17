lxc=${lxc:-"{{uid}}"}
db_host="{{db_host}}"
db_name="{{uid}}"

# env config
cat <<EOF | {{ssh}} $lxc "cat > {{config}}"
{{>config.sh}}
EOF

# run init
path=tpl/init
if [ -d $path ]; then
    cd $path
    git pull origin init
else
    mkdir $path
    cd $path
    git clone -b init --single-branch git@github.com:superdesk/fireq.git .
fi
if [ -f {{uid}}.sh ]; then
    cfg={{uid}}
elif [ -f {{scope}}.sh ]; then
    cfg={{scope}}
else
    cfg=sd
fi
cd ../../
./fire r -s {{scope}} init/$cfg | {{ssh}} $lxc
unset cfg path

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

[ -z "${pubapi-}" ] || (
{{>pubapi.sh}}
)
EOF2
