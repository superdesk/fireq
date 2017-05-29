name=$name
start=${start-}
[ -z "$start" ] || lxc-start -n $name
lxc-wait -n $name -s RUNNING
while ! timeout 1 bash -c "</dev/tcp/$name/22" &> /dev/null; do sleep 3; done
