{{>init/sd.sh}}

cat <<"EOF" >> {{config}}
WEBHOOK_PERSONALIA_AUTH=1234
EOF
