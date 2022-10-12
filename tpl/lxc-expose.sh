lxc ls --format compact
[ -n "{{clean}}" ] && iptables -t nat -F PREROUTING
lxc=$(lxc exec {{name}} -- hostname -I)
iptables -t nat -A PREROUTING -p tcp --dport 80 -j DNAT -i eth0 -d {{domain}} --to $lxc
iptables -L -vt nat
