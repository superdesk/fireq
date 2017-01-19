### deploy
## env.sh
envfile={{repo_env}}.sh
[ -f $envfile ] || cat << "EOF" > $envfile
{{>deploy-env.sh}}
EOF

## load env.sh and custom settings in activation script
config={{config}}
activate={{repo_env}}/bin/activate
grep "$envfile" $activate || cat << EOF >> $activate
set -a
[ -f $config ] && . $config
. $envfile
set +a
EOF
unset envfile config activate

## prepare dist directory
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
