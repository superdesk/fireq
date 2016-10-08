#!/bin/sh
set -e

[ -n "$delete" ] && (lxc-stop -n ${name}; lxc-destroy -n ${name})

lxc-create -t download -n ${name} -- -d ubuntu -r xenial -a amd64 &&
lxc-start -n ${name} &&
sleep 5 && lxc-attach --clear-env -n ${name} -- /bin/sh -c "
    DEBIAN_FRONTEND=noninteractive
    apt-get install -y openssh-server
" &&
cat ~/.ssh/id_rsa.pub | lxc-attach -n ${name} -- /bin/sh -c "
    /bin/mkdir -p /root/.ssh;
    /bin/cat > /root/.ssh/authorized_keys
" &&
echo "********************************"
echo "Go to container:"
echo "$ ssh root@$(lxc-info -n ${name} -iH)"
echo "********************************"
