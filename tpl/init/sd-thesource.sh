{{>init/sd.sh}}

cat <<"EOF" >> {{config}}
MAIL_SERVER=10.0.3.1
EOF
