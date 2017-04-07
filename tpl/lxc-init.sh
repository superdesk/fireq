proj={{name}}
name=${name:-$proj}
opts=${opts:-}
authorized_keys=${authorized_keys:-}
mount_src=${mount_src:-}
mount_cache=${mount_cache:-}

lxc-create -t download -n $name $opts -- -d ubuntu -r xenial -a amd64

[ -z "$mount_src" ] || cat <<EOF >> /var/lib/lxc/$name/config
lxc.mount.entry = $mount_src opt/$proj none bind,create=dir
EOF

[ -z "$mount_cache" ] || (
    log=$mount_cache/log/$name
    mkdir -p $mount_cache/{pip,npm,dpkg} $log
    cat <<EOF >> /var/lib/lxc/$name/config
lxc.mount.entry = $mount_cache/pip root/.cache/pip/ none bind,create=dir
lxc.mount.entry = $mount_cache/npm root/.npm none bind,create=dir
lxc.mount.entry = $mount_cache/dpkg var/cache/apt/archives/ none bind,create=dir
lxc.mount.entry = $log var/log/$proj none bind,create=dir
EOF
)

lxc-start -n $name
sleep 5

lxc_attach="lxc-attach --clear-env -n $name -- /bin/bash"
cat <<"EOF" | $lxc_attach
set -exuo pipefail

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y --no-install-recommends openssh-server openssl curl
EOF

if [ -n "$authorized_keys" ]; then
    cat $authorized_keys | $lxc_attach -c "
/bin/mkdir -p /root/.ssh
/bin/cat > /root/.ssh/authorized_keys
"
else
    # use password-less root login instead
    cat <<"EOF" | $lxc_attach
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
fi
