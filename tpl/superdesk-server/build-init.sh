#branch=1.4
{{>superdesk-dev/build-init.sh}}

rm -rf {{repo}}/server-core
{{>superdesk/build-init.sh}}
