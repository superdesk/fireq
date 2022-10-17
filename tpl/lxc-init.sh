proj={{name}}
name=${name:-$proj}
opts=${opts:-}
mount_src=${mount_src:-}
mount_cache=${mount_cache:-}
mount_ssh=${mount_ssh:-}
authorized_keys=${authorized_keys:-}
no_login=${no_login:-}

lxc init images:ubuntu/20.04 $name -c 'security.privileged=true'

[ -z "$mount_ssh" ] || lxc config device add $name ssh disk source=/root/.ssh path=root/.ssh


[ -z "$mount_src" ] || lxc config device add $name src disk source=${mount_src} path=opt/${proj}

[ -z "$mount_cache" ] || (
    log=$mount_cache/log/$name
    mkdir -p $mount_cache/{pip,npm,dpkg} $log
    lxc config device add $name log disk source=${log} path=var/log/${proj}

)

lxc start $name
sleep 5

lxc_attach="lxc exec $name -- /bin/bash"
cat <<"EOF" | $lxc_attach
set -exuo pipefail

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y --no-install-recommends openssh-server curl ca-certificates

# disable banner after login
touch ~/.hushlogin
EOF

# put authorized_keys into container
[ -z "$authorized_keys" ] || cat $authorized_keys | $lxc_attach -c "
/bin/mkdir -p /root/.ssh
/bin/cat > /root/.ssh/authorized_keys
"

# use password-less root login if no $authorized_keys and no $mount_ssh
[ -n "$mount_ssh" ] || [ -n "$authorized_keys" ] || cat <<"EOF" | $lxc_attach
set -exuo pipefail

passwd -d root
sed -i \
    -e 's/^#*\(PermitRootLogin\) .*/\1 yes/' \
    -e 's/^#*\(PasswordAuthentication\) .*/\1 yes/' \
    -e 's/^#*\(PermitEmptyPasswords\) .*/\1 yes/' \
    -e 's/^#*\(UsePAM\) .*/\1 no/' \
    /etc/ssh/sshd_config
systemctl restart sshd
EOF

[ -n "$no_login" ] || (
{{>lxc-wait.sh}}


{{ssh}} "$(lxc exec $name -- hostname -I)"
)
