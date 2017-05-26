#branch=1.4
{{>superdesk/build-src-dev.sh}}

repo={{repo}}/server-core
rm -rf $repo
{{>superdesk/build-src.sh}}
