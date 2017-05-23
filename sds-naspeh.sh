{{>init/sd.sh}}

cat <<"EOF" >> {{config}}
{{>init/.amazon.sh}}
AMAZON_CONTAINER_NAME='sd-frankfurt-test'
AMAZON_REGION=eu-central-1
EOF
