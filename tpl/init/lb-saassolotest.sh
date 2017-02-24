{{>init/lb.sh}}

cat <<"EOF" >> {{config}}
SUBSCRIPTION_LEVEL=solo
EOF
