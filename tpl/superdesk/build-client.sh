## client part
{{>add-node.sh}}

cd {{repo_client}}
npm install grunt-cli
time npm install

# TODO: maybe remove "--force" later
# vars are used in "webpack.config.js"
time \
SUPERDESK_URL='<SUPERDESK_URL>' \
SUPERDESK_WS_URL='<SUPERDESK_WS_URL>' \
SUPERDESK_RAVEN_DSN='<RAVEN_DSN>' \
IFRAMELY_KEY='<IFRAMELY_KEY>' \
PUBLISHER_API_DOMAIN='<PUBLISHER_API_DOMAIN>' \
PUBLISHER_API_SUBDOMAIN='<PUBLISHER_API_SUBDOMAIN>' \
grunt build{{#dev}} --force{{/dev}}
