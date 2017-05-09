{{>init/sd.sh}}

cat <<"EOF" >> {{config}}
DB_HOST=data-sd--elastic2

{{>init/.amazon.sh}}
AMAZON_CONTAINER_NAME='sd-frankfurt-test'
AMAZON_REGION=eu-central-1
EOF

cat <<"EOF" > /etc/nginx/conf.d/media.inc
# serve directly from amazon
location /api/upload-raw/ {
    rewrite ^/api/upload-raw/(.*)$ https://sd-frankfurt-test.s3-eu-central-1.amazonaws.com/sd-naspeh/$1;
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
