cat <<"EOF" >> {{config}}
{{>init/.liveblog.sh}}
EOF

[[ "$(hostname)" =~ ^lb-syndtest ]] && cat <<"EOF" >> {{config}}
SYNDICATION=true
EOF
