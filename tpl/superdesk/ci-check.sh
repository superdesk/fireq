lxc="{{lxc_www}}--{{target}}";
./fire lxc-copy -cs -b {{lxc_build}} $lxc
cat <<"EOF2" | {{ssh}} $lxc
{{{inner}}}
EOF2
