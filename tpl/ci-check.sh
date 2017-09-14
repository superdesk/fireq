lxc="{{uid}}--{{target}}";
lxc-destroy -fn $lxc || true
lxc-copy -s -n {{lxc_build}} -N $lxc
cat <<"EOF" >>  /var/lib/lxc/$lxc/config
# keep some processes free for other stuff like mongo, etc.
# host7: use 8 cores from 12
lxc.cgroup.cpuset.cpus = 0-7
EOF
./fire lxc-wait --start $lxc
cat <<"EOF2" | {{ssh}} $lxc
{{{inner}}}
EOF2
