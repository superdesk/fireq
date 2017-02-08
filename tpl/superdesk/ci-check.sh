lxc="{{uid}}--{{target}}";
./fire lxc-copy --cpu="0-5" -cs -b {{lxc_build}} $lxc
cat <<"EOF2" | {{ssh}} $lxc
{{{inner}}}
EOF2
./fire lxc-rm $lxc
