name=$name
start=${start-}
[ -z "$start" ] || lxc start $name
# lxc-wait -n $name -s RUNNING -- no longer needed since lxd already has that functionality.
while ! timeout 1 bash -c "</dev/tcp/$(lxc exec $name -- hostname -I | xargs -r)/22" &> /dev/null; do sleep 3; done