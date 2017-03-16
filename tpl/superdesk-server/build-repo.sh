branch=1.4
{{>superdesk-dev/build-repo.sh}}

rm -rf {{repo}}/server-core
{{>superdesk/build-repo.sh}}
