{{>init/lb.sh}}

cat <<"EOF" >> {{config}}
SUBSCRIPTION_LEVEL=team
EOF
