[ -z "{{start}}" ] || lxc-start -n {{name}}
lxc-wait -n {{name}} -s RUNNING
while ! $(./fire2 lxc-ssh {{name}} -c true > /dev/null)
    do sleep 2
done
