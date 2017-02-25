name=$name
src=$src_dir
cache=$cache_dir

lxc-create -t download -n $name -- -d ubuntu -r xenial -a amd64

mkdir -p $cache/{pip,npm,dpkg}
cat <<EOF >> /var/lib/lxc/$name/config;
lxc.mount.entry = $src opt/{{name}} none bind,create=dir
lxc.mount.entry = $cache/pip root/.cache/pip/ none bind,create=dir
lxc.mount.entry = $cache/npm root/.npm none bind,create=dir
lxc.mount.entry = $cache/dpkg var/cache/apt/archives/ none bind,create=dir
EOF

lxc-start -n $name
sleep 5

cat <<"EOF2" | lxc-attach --clear-env -n $name -- /bin/bash
{{>header.sh}}
apt-get update
apt-get install -y --no-install-recommends openssh-server openssl curl

# use password-less root login for development
passwd -d root
sed -i \
    -e 's/^#*\(PermitRootLogin\) .*/\1 yes/' \
    -e 's/^#*\(PasswordAuthentication\) .*/\1 yes/' \
    -e 's/^#*\(PermitEmptyPasswords\) .*/\1 yes/' \
    -e 's/^#*\(UsePAM\) .*/\1 no/' \
    /etc/ssh/sshd_config
systemctl restart sshd
EOF2
