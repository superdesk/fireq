{{>init/sd.sh}}

cat <<"EOF" >> {{config}}
{{>init/.amazon.sh}}
EOF
