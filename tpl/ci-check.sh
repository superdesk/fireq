lxc="{{uid}}--{{target}}";
lxc-destroy -fn $lxc || true
lxc-copy -s -n {{lxc_build}} -N $lxc
echo "lxc.cgroup.cpuset.cpus = 0-5" >> /var/lib/lxc/$lxc/config
./fire lxc-wait --start $lxc
cat <<"EOF2" | {{ssh}} $lxc
{{{inner}}}
EOF2
lxc-destroy -fn $lxc
