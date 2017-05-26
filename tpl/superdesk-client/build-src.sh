#branch=1.4
{{>superdesk/build-src-dev.sh}}

repo={{repo}}/client-core
rm -rf $repo
{{>superdesk/build-src.sh}}
