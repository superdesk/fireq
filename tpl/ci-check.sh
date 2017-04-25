lxc="{{uid}}--{{target}}";
lxc-destroy -fn $lxc || true
lxc-copy -s -n {{lxc_build}} -N $lxc
# keep some processes free for other stuff (host7: use 8 from 12)
echo "lxc.cgroup.cpuset.cpus = 0-7" >> /var/lib/lxc/$lxc/config
./fire lxc-wait --start $lxc
cat <<"EOF2" | {{ssh}} $lxc
{{{inner}}}
EOF2
