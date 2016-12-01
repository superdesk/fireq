#!/bin/sh
set -ex

base=${base:-'base-sd'}
clean=${clean-1}
start=${start-1}
[ -z "$rename" ] || rename='--rename'
[ -z "${snapshot-1}" ] || snapshot='-s'

if [ -n "$clean" ] && lxc-info -n $name -sH; then
    lxc-destroy -f -n $name || true
fi

exist=$(lxc-info -n $name -sH || echo '')
if [ -z "$exist" ]; then
    lxc-stop -n $base && base_stoped=1 || true
    lxc-copy -n $base -N $name $rename $snapshot
    [ -n "$base_stoped" ] && [ -z "$rename" ] && lxc-start -n $base
    exist='STOPPED'
    [ -n "$cpus" ] && echo "lxc.cgroup.cpuset.cpus = $cpus" >> /var/lib/lxc/$name/config
fi

start=$([ -n "$start" ] && [ "$exist" = "STOPPED" ] && echo 1 || echo '')
if [ -n "$start"  ] ; then
    lxc-start -n $name
    lxc-wait -n $name -s RUNNING;
    ./fire lxc-wait $name
fi
