{{>init/sd.sh}}

cat <<"EOF" > {{repo_client}}/dist/config.*.js
window.superdeskConfig = {
    features: {
        swimlane: {columnsLimit: 4},
        editor3: true
    }
};
EOF
