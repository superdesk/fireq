[ -z "{{start}}" ] || lxc-start -n {{name}}
lxc-wait -n {{name}} -s RUNNING
while ! timeout 1 bash -c "cat < /dev/null > /dev/tcp/{{name}}/22"
    do sleep 3
done
