lxc={{lxc_build}}

# exit if cleaning is not needed and build container stopped
# stopped should mean that previous build was successful
[ -z "{{clean_build}}" ] && [ $(lxc-info -n $lxc -sH) == 'STOPPED' ] && exit 0

# clean previous containers
(lxc-ls -1\
    | grep "^{{uid}}--"\
    | grep -v "^{{lxc_build}}$"\
    | sort -r\
    | xargs -r ./fire lxc-rm) || true
./fire lxc-rm {{lxc_build}} || true

# create new container and build code
./fire lxc-copy -sc -b {{lxc_base}} $lxc
cat <<"EOF2" | {{ssh}} $lxc
{{>header.sh}}
{{>build.sh}}
EOF2
lxc-stop -n $lxc
