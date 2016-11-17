#!/bin/sh
set -ex

base=${base:-'sdbase'}
clean=${clean-1}
start=${start-1}

if [ -n "$clean" ]; then
    lxc-stop -n $name || true
    lxc-destroy -n $name || true
fi

exist=$(lxc-info -n $name -sH || echo '')
if [ -z "$exist" ]; then
    lxc-stop -n $base && base_stoped=1 || true
    lxc-copy -n $base -N $name
    [ -n "$base_stoped" ] && lxc-start -n $base
    exist='STOPPED'
fi

start=$([ -n "$start" ] && [ "$exist" = "STOPPED" ] && echo 1 || echo '')
if [ -n "$start"  ] ; then
    lxc-start -n $name
    lxc-wait -n $name -s RUNNING;
    ./fire lxc-wait $name
fi
