### Client part
{{>add-node.sh}}

cd {{repo_client}}
npm i grunt-cli
npm i bower
time npm install
time bower --allow-root install

# export VIEW_DATE_FORMAT='<VIEW_DATE_FORMAT>'
# export VIEW_TIME_FORMAT='<VIEW_TIME_FORMAT>'
time \
SUPERDESK_URL='<SUPERDESK_URL>' \
SUPERDESK_WS_URL='<SUPERDESK_WS_URL>' \
SUPERDESK_RAVEN_DSN='<RAVEN_DSN>' \
IFRAMELY_KEY='<IFRAMELY_KEY>' \
EMBEDLY_KEY='<EMBEDLY_KEY>' \
grunt build --force
