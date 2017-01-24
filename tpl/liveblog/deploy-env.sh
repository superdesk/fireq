{{>superdesk/deploy-env.sh}}

### Liveblog custom
S3_THEMES_PREFIX=${S3_THEMES_PREFIX:-"/$(hostname)/"}
EMBEDLY_KEY=${EMBEDLY_KEY:-}
