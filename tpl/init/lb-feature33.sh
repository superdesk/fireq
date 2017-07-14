cat <<"EOF" >> {{config}}
{{>init/.liveblog.sh}}
EOF

cat <<EOF >> {{config}}
SYNDICATION=true
EOF
