# prepare dist directory
_activate
dist_orig={{repo_client}}/dist
dist=${dist_orig}-deploy
rm -rf $dist
cp -r $dist_orig $dist
cd $dist

filename=(app.bundle.*)
# there no app.bundle.js for 3.0.9 version
[ -f $filename ] || filename=index.html

sed -i \
    -e "s|<SUPERDESK_URL>|http$SSL://$HOST/api|" \
    -e "s|<SUPERDESK_WS_URL>|ws$SSL://$HOST/ws|" \
    -e "s|<IFRAMELY_KEY>|${IFRAMELY_KEY:-}|" \
    -e "s|<RAVEN_DSN>|${RAVEN_DSN:-}|" \
    -e "s|<EMBEDLY_KEY>|${EMBEDLY_KEY:-}|" \
    -e "s|<SYNDICATION>|${SYNDICATION:-}|" \
    $filename
unset dist_orig dist filename
