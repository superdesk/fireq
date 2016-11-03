#!/bin/sh
set -e

root=$(dirname $(dirname $(realpath -s $0)))
name=${name:-'master'}
lxc=${lxc:-"sd-$name"}
clean=${clean:-}
endpoint=${endpoint:-'superdesk-dev/master'}

if [ -n "$clean" ]; then
    lxc-stop -n sd-base || true
    lxc-stop -n $lxc || true
    lxc-destroy -n $lxc || true
    lxc-copy -n sd-base -N $lxc
    lxc-start -n $lxc
    sleep 5
fi
cd $root
#export repo_branch=ntb
./fire r -e $endpoint -a do_gh_push
