#!/bin/sh
set -ex

[ -n "$rm" ] && (lxc-stop -n $name; lxc-destroy -n $name) || true

lxc-create -t download -n $name $opts -- -d ubuntu -r xenial -a amd64
lxc-start -n $name
sleep 5
lxc-attach --clear-env -n $name -- /bin/sh -c "
    DEBIAN_FRONTEND=noninteractive
    apt-get update;
    apt-get install -y --no-install-recommends openssh-server rsync curl wget
"
cat ${keys:-"/root/.ssh/id_rsa.pub"} | lxc-attach --clear-env -n $name -- /bin/sh -c "
    /bin/mkdir -p /root/.ssh;
    /bin/cat > /root/.ssh/authorized_keys
"
cat <<EOF
**********************************************************************
Go to container:
$ ssh -o 'StrictHostKeyChecking no' root@$(lxc-info -n $name -iH)
**********************************************************************
EOF
