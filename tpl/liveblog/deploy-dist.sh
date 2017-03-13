# prepare dist directory
_activate
dist_orig={{repo_client}}/dist
dist=${dist_orig}-deploy
rm -rf $dist
cp -r $dist_orig $dist
if [ -f bower.json ]; then
    filename=$dist/index.html
else
    filename=$dist/app.bundle.*
fi
sed -i \
    -e "s|<SUPERDESK_URL>|http$SSL://$HOST/api|" \
    -e "s|<SUPERDESK_WS_URL>|ws$SSL://$HOST/ws|" \
    -e "s|<IFRAMELY_KEY>|${IFRAMELY_KEY:-}|" \
    -e "s|<RAVEN_DSN>|${RAVEN_DSN:-}|" \
    -e "s|<PUBLISHER_API_DOMAIN>|${PUBLISHER_API_DOMAIN:-}|" \
    -e "s|<EMBEDLY_KEY>|${EMBEDLY_KEY:-}|" \
    -e "s|<SYNDICATION>|${SYNDICATION:-}|" \
    $filename
unset dist_orig dist filename
