{{>init/sd.sh}}

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

_activate
pip install -e git+https://github.com/superdesk/superdesk-core.git@1.6#egg=Superdesk-Core
