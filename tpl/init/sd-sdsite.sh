{{>init/sd.sh}}

cat <<"EOF" >> {{config}}
{{>init/.amazon-from-dev.sh}}

PUBLISHER_API_DOMAIN=master.s-lab.sourcefabric.org
EOF
