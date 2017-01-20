# clean previous containers
(lxc-ls -1\
    | grep "^{{lxc_www}}--"\
    | grep -v "^{{lxc_build}}$"\
    | sort -r\
    | xargs -r ./fire lxc-rm) || true
./fire lxc-rm {{lxc_build}}

# create new container and build code
lxc={{lxc_build}}
./fire lxc-copy -sc -b {{lxc_base}} $lxc
cat <<"EOF2" | {{ssh}} $lxc
{{>header.sh}}
{{>build.sh}}
EOF2
lxc-stop -n $lxc
