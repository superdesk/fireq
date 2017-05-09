{{>init/sd.sh}}

cat <<"EOF" > {{repo_client}}/dist/config.*.js
window.superdeskConfig = {
    features: {
        swimlane: {columnsLimit: 4},
        editor3: true
    }
};
EOF

cat <<"EOF" >> {{config}}
DB_HOST=data-sd--elastic2

{{>init/.amazon.sh}}
AMAZON_CONTAINER_NAME='sd-frankfurt-test'
AMAZON_REGION=eu-central-1
# relative media urls
MEDIA_PREFIX=/sd-master
EOF

cat <<"EOF" > /etc/nginx/conf.d/media.inc
location /sd-master/ {
    return 302 https://sd-frankfurt-test.s3-eu-central-1.amazonaws.com$request_uri;
}
EOF
