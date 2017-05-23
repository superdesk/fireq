{{>init/sd.sh}}

cat <<"EOF" >> {{config}}
{{>init/.amazon.sh}}

PUBLISHER_API_DOMAIN=sourcefabric.org
PUBLISHER_API_SUBDOMAIN=master.s-lab
EOF
