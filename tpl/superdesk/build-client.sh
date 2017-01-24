## client part
{{>add-node.sh}}

cd {{repo_client}}
npm install grunt-cli
time npm install

# TODO: maybe remove "--force" later
# vars are used in "webpack.config.js"
# export VIEW_DATE_FORMAT='<VIEW_DATE_FORMAT>'
# export VIEW_TIME_FORMAT='<VIEW_TIME_FORMAT>'
time \
SUPERDESK_URL='<SUPERDESK_URL>' \
SUPERDESK_WS_URL='<SUPERDESK_WS_URL>' \
SUPERDESK_RAVEN_DSN='<RAVEN_DSN>' \
IFRAMELY_KEY='<IFRAMELY_KEY>' \
grunt build --force
