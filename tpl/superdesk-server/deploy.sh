{{>superdesk/deploy.sh}}

# generate docs
cat <<"EOF" | sh || true
{{>check-docs.sh}}
EOF
