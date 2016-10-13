#!/bin/sh
set -ex
lxc-ls --fancy
iptables -t nat -F PREROUTING
iptables -t nat -A PREROUTING\
    -p tcp --dport 80 -j DNAT -i eth0 -d $domain\
    --to $(lxc-info -n $name -iH)
iptables -L -vt nat
