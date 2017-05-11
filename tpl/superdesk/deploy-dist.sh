# prepare dist directory
dist_orig={{repo_client}}/dist
dist=${dist_orig}-deploy
rm -rf $dist
cp -r $dist_orig $dist

#load env variables needed for config.js
. $honcho_env
configjs=$(ls $dist | grep -E "config.\w+.js")
cat <<EOF > $dist/$configjs
{{>add-config.js}}
EOF

unset dist_orig dist configjs
