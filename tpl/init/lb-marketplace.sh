{{>init/lb.sh}}

cat <<"EOF" >> {{config}}
MARKETPLACE=true
EOF
