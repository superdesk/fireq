cat <<"EOF" >> {{config}}
{{>init/.liveblog.sh}}
EOF

cat <<EOF >> {{config}}
SYNDICATION=true
MARKETPLACE=true
MARKETPLACE_APP_URL=https://market.liveblog.pro/api
EOF
