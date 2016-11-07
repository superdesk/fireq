#!/bin/sh
set -ex

base=${base:-'sd-base'}
secs=${secs-5}
clean=${clean-1}

if [ -n "$clean" ]; then
    lxc-stop -n $name || true
    lxc-destroy -n $name || true
fi

exist=$(lxc-info -n $name -sH || echo '')
if [ -z "$exist" ]; then
    lxc-stop -n $base && base_stoped=1 || true
    lxc-copy -n $base -N $name
    lxc-start -n $name
    [ -n "$base_stoped" ] && lxc-start -n $base
    [ -n "$secs" ] && sleep $secs
fi
