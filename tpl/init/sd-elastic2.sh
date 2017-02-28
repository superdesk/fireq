{{>init/sd.sh}}

cat <<"EOF" >> {{config}}
DB_HOST=data-sd--elastic2
EOF
