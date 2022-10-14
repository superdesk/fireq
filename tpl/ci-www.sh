lxc="{{uid}}--www";

lxc delete -f $lxc || true
lxc copy {{lxc_build}} $lxc
lxc delete -f {{lxc_build}}
./fire lxc-wait --start $lxc

{{>ci-deploy.sh}}

lxc stop $lxc
lxc delete -f {{uid}} || true
lxc copy $lxc {{uid}} 

# mount logs directory
mkdir -p {{host_logs}}
logs={{logs}}
# it works differently in lxd since it stores everything in its sqlite db - no static configs.
lxc config device add {{uid}} logs disk source={{host_logs}} path=${logs:1}
#cat <<EOF >> /var/lib/lxc/{{uid}}/config;
#lxc.mount.entry = {{host_logs}} ${logs:1} none bind,create=dir
#EOF
lxc start {{uid}};
./fire ci-nginx || true

nginx -s reload
