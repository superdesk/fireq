{{>init/sd.sh}}

cat <<"EOF" >> {{config}}
DB_HOST=data-sd--elastic2
DB_NAME=sd-naspeh--2

{{>init/.amazon.sh}}
AMAZON_CONTAINER_NAME='sd-frankfurt-test'
AMAZON_REGION=eu-central-1
# relative media urls
MEDIA_PREFIX=/sd-naspeh
EOF

cat <<"EOF" > /etc/nginx/conf.d/media.inc
location /sd-naspeh/ {
    return 302 https://sd-frankfurt-test.s3-eu-central-1.amazonaws.com$request_uri;
}
EOF

set +x
. {{config}}
set -x

cat <<EOF > {{repo_client}}/dist/config.*.js
window.superdeskConfig = {
    server: {
        url: location.origin + '/api',
        ws: 'ws' + location.origin.slice(4) + '/ws'
    },
    iframely: {key: '$IFRAMELY_KEY'},
    features: {
        swimlane: {columnsLimit: 4},
        editor3: true
    }
};
EOF

#_activate
#pip install -e git+https://github.com/superdesk/superdesk-core.git@1.6#egg=Superdesk-Core
