cat <<"EOF" >> {{config}}
{{>init/.liveblog.sh}}

SYNDICATION=true
MARKETPLACE=true
MARKETPLACE_APP_URL=https://market.liveblog.pro/api
EOF
