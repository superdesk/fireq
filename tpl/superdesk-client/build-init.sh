#branch=1.4
{{>superdesk-dev/build-init.sh}}

rm -rf {{repo}}/client-core
{{>superdesk/build-init.sh}}

chunks=/var/tmp/e2e-chunks.py
cat <<"EOF" > $chunks
{{>e2e-chunks.py}}
EOF
python3 $chunks
unset chunks
