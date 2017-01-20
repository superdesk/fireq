### deploy
# env.sh
envfile={{repo_env}}.sh
cat <<"EOF" > $envfile
{{>deploy-env.sh}}
EOF

# write config if not exist
config={{config}}
[ -f $config ] || cat <<EOF > $config
HOST=${HOST:-'{{host}}'}
HOST_SSL=${HOST_SSL:-'{{host_ssl}}'}

MONGO_URI=mongodb://{{db_host}}/{{db_name}}
LEGAL_ARCHIVE_URI=\${MONGO_URI}_la
ARCHIVED_URI=\${MONGO_URI}_ar
CONTENTAPI_MONGO_URI=\${MONGO_URI}_ca

ELASTICSEARCH_URL=http://{{db_host}}:9200
ELASTICSEARCH_INDEX={{db_name}}
CONTENTAPI_ELASTICSEARCH_INDEX=\${ELASTICSEARCH_INDEX}_ca
EOF

# load env.sh and config in activation script
activate={{repo_env}}/bin/activate
grep "$envfile" $activate || cat <<EOF >> $activate
set -a
[ -f $config ] && . $config
. $envfile
set +a
EOF
unset envfile activate config


# prepare dist directory
_activate
dist_orig={{repo_client}}/dist
dist=${dist_orig}-deploy
rm -rf $dist
cp -r $dist_orig $dist
sed -i \
    -e "s|<SUPERDESK_URL>|http$SSL://$HOST/api|" \
    -e "s|<SUPERDESK_WS_URL>|ws$SSL://$HOST/ws|" \
    -e "s|<IFRAMELY_KEY>|${IFRAMELY_KEY:-}|" \
    -e "s|<EMBEDLY_KEY>|${EMBEDLY_KEY:-}|" \
    -e "s|<RAVEN_DSN>|${RAVEN_DSN:-}|" \
{{#is_superdesk}}
    $dist/app.bundle.*
{{/is_superdesk}}
{{^is_superdesk}}
    $dist/index.html
{{/is_superdesk}}
unset dist_orig dist


{{>add-nginx.sh}}


{{>add-supervisor.sh}}
{{#dev}}
{{>add-smtp.sh}}
{{/dev}}
