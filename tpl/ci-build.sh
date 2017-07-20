lxc={{lxc_build}}

# exit if cleaning is not needed and build container stopped
# stopped should mean that previous build was successful
[ -z "{{clean_build}}" ] && [ "$(lxc-info -n $lxc -sH)" == 'STOPPED' ] && exit 0

# clean previous containers
(lxc-ls -1\
    | grep "^{{uid}}--"\
    | grep -v "^$lxc$"\
    | sort -r\
    | xargs -r -L1 lxc-destroy -fn) || true
lxc-destroy -fn $lxc || true

# create new container and build code
lxc-copy -s -n {{lxc_base}} -N $lxc
{{#priv_repo_remote}}
cp /root/.ssh/* /var/lib/lxc/$lxc/rootfs/root/.ssh/
{{/priv_repo_remote}}
./fire lxc-wait --start $lxc
cat <<"EOF2" | {{ssh}} $lxc
{{>header.sh}}
{{>build.sh}}
EOF2
lxc-stop -n $lxc
