envfile={{repo}}/env.sh
[ -f $envfile ] || cat << "EOF" > $envfile
{{>env.sh}}
EOF

config={{config}}
activate={{repo_env}}/bin/activate
grep "$envfile" $activate || cat << EOF >> $activate
set -a
[ -f $config ] && . $config
. $envfile
set +a
EOF
unset envfile config activate

_activate
dist_orig={{repo_client}}/dist
dist=${dist_orig}-deploy
rm -rf $dist
cp -r $dist_orig $dist
sed -i \
    -e "s|<SUPERDESK_URL>|http$SSL://$HOST/api|" \
    -e "s|<SUPERDESK_WS_URL>|ws$SSL://$HOST/ws|" \
    -e "s|<IFRAMELY_KEY>|${IFRAMELY_KEY:-}|" \
    -e "s|<RAVEN_DSN>|${RAVEN_DSN:-}|" \
    $dist/app.bundle.*
unset dist_orig dist


### prepopulate
cd {{repo_server}}
[ -z "${sample_data:-1}" ] || sample_data='--sample-data'
python manage.py app:initialize_data --help | grep -- --sample-data && sample_data=$sample_data || sample_data=

python manage.py app:initialize_data $sample_data
python manage.py users:create -u admin -p admin -e 'admin@example.com' --admin


### nginx
{{>add-nginx.sh}}

path=/etc/nginx/conf.d
cat << "EOF" > $path/params.conf
{{>nginx-params.conf}}
EOF

cat << EOF > $path/default.conf
{{>nginx.conf}}
EOF
unset path
nginx -s reload


### supervisor
apt-get -y install supervisor

logs=/var/log/{{name}}
[ -d $logs ] || mkdir $logs

path=/etc/supervisor/conf.d/{{name}}.conf
cat << "EOF" > $path
{{>supervisor.conf}}
EOF

systemctl enable supervisor
systemctl restart supervisor
