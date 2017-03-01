cat <<EOF > {{repo}}/client-core/scripts/config.js
window.superdeskConfig = {
    server: {
        url: location.origin + '/api',
        ws: 'ws' + location.origin.slice(4) + '/ws'
    },
    iframely: {key: '$IFRAMELY_KEY'}
};
EOF
