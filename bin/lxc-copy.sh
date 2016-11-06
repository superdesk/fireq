#!/bin/sh
set -ex

from=${from:-'sd-base'}

lxc-stop -n $from || true
lxc-stop -n $name || true
lxc-destroy -n $name || true
lxc-copy -n $from -N $name
lxc-start -n $name
