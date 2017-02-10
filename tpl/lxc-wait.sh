[ -z "{{start}}" ] || lxc-start -n {{name}}
lxc-wait -n {{name}} -s RUNNING
while ! $(./fire lxc-ssh {{name}} -c true > /dev/null)
    do sleep 3
done
