{{>init/lb.sh}}

cat <<EOF >> {{config}}
SYNDICATION=true
MARKETPLACE=true
MARKETPLACE_APP_URL=https://market.liveblog.pro/api
EOF
