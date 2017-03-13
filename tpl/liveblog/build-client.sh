### Client part
{{>add-node.sh}}

cd {{repo_client}}
npm i grunt-cli
time npm install

if [ -f bower.json ]; then
    # 3.0.9, 3.1.0 versions need bower
    npm i bower
    time bower --allow-root install
fi

time \
SUPERDESK_URL='<SUPERDESK_URL>' \
SUPERDESK_WS_URL='<SUPERDESK_WS_URL>' \
SUPERDESK_RAVEN_DSN='<RAVEN_DSN>' \
IFRAMELY_KEY='<IFRAMELY_KEY>' \
EMBEDLY_KEY='<EMBEDLY_KEY>' \
SYNDICATION='<SYNDICATION>' \
grunt build --force
