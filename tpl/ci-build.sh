lxc={{lxc_build}}

# exit if cleaning is not needed and build container stopped
# stopped should mean that previous build was successful
[ -z "{{clean_build}}" ] && [ "$(lxc ls -c s --format csv $lxc)" == 'STOPPED' ] && exit 0

# clean previous containers
(lxc ls -c n --format csv\
    | grep "^{{uid}}--"\
    | grep -v "^$lxc$"\
    | sort -r\
    | xargs -r -L1 lxc delete -f) || true
lxc delete -f $lxc || true

# create new container and build code
lxc copy {{lxc_base}} $lxc
./fire lxc-wait --start $lxc
cat <<"EOF2" | {{ssh}} $lxc
{{>header.sh}}
{{>build.sh}}
EOF2
lxc stop $lxc

