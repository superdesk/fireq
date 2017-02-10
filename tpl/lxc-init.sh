name={{name}}
lxc-create -t download -n $name {{opts}} -- -d ubuntu -r xenial -a amd64
lxc-start -n $name
sleep 5
lxc-attach --clear-env -n $name -- /bin/sh -c "
    DEBIAN_FRONTEND=noninteractive
    apt-get update;
    apt-get install -y --no-install-recommends openssh-server openssl curl
"
cat {{keys}} | lxc-attach --clear-env -n $name -- /bin/sh -c "
    /bin/mkdir -p /root/.ssh;
    /bin/cat > /root/.ssh/authorized_keys
"
cat <<EOF
**********************************************************************
Go to container:
$ ssh -o StrictHostKeyChecking=no root@$(lxc-info -n $name -iH)
**********************************************************************
EOF
