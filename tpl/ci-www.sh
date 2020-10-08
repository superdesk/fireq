lxc="{{uid}}--www";

lxc-destroy -fn $lxc || true
lxc-copy -s -n {{lxc_build}} -N $lxc
./fire lxc-wait --start $lxc

{{>ci-deploy.sh}}

lxc-stop -n $lxc
lxc-destroy -fn {{uid}} || true
lxc-copy -n $lxc -N {{uid}} -R

# mount logs directory
mkdir -p {{host_logs}}
logs={{logs}}
cat <<EOF >> /var/lib/lxc/{{uid}}/config;
lxc.mount.entry = {{host_logs}} ${logs:1} none bind,create=dir
EOF
lxc-start -n {{uid}};
./fire ci-nginx || true
