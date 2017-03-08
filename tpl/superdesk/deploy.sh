### deploy
# write config if not exist
config={{config}}
[ -f $config ] || cat <<EOF > $config
{{>deploy-config.sh}}
EOF

# env.sh
envfile={{repo}}/env.sh
cat <<"EOF" > $envfile
{{>deploy-env.sh}}
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
_activate

{{>deploy-dist.sh}}


{{>add-nginx.sh}}


{{>add-supervisor.sh}}


[ -z "${add_smtp:-1}" ] || (
{{>add-smtp.sh}}
)

{{>prepopulate.sh}}
