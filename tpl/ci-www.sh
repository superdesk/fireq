lxc="{{uid}}--www";

lxc-destroy -fn $lxc || true
lxc-copy -s -n {{lxc_build}} -N $lxc
./fire lxc-wait --start $lxc

deploy() {
    {{>ci-deploy.sh}}
}

# workaround to stop deploy on error but let the script continue
# so it will destroy the old container and make the error visible
error=0
deploy &
wait $! || {
    error=$?
}

lxc-stop -n $lxc
lxc-destroy -fn {{uid}} || true

if [ "$error" -eq "0" ]; then
    lxc-copy -n $lxc -N {{uid}} -R
else
    exit $error
fi

# mount logs directory
mkdir -p {{host_logs}}
logs={{logs}}
cat <<EOF >> /var/lib/lxc/{{uid}}/config;
lxc.mount.entry = {{host_logs}} ${logs:1} none bind,create=dir
EOF
lxc-start -n {{uid}};
./fire ci-nginx || true
