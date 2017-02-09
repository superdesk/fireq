lxc-ls --fancy
[ -n "{{clean}}" ] && iptables -t nat -F PREROUTING
lxc=$(lxc-info -n {{name}} -iH)
iptables -t nat -A PREROUTING -p tcp --dport 80 -j DNAT -i eth0 -d {{domain}} --to $lxc
iptables -L -vt nat
