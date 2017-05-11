## client part
{{>add-node.sh}}

cd {{repo_client}}
npm install grunt-cli
time npm install

# TODO: maybe remove "--force" later
# vars are used in "webpack.config.js"
time \
grunt build{{#dev}} --force{{/dev}}
