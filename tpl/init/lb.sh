cat <<"EOF" >> {{config}}
{{>init/.liveblog.sh}}
EOF

cat <<EOF >> {{config}}
SYNDICATION=$([[ "$(hostname)" =~ ^lb-syndtest ]] && echo true || echo)
EOF
