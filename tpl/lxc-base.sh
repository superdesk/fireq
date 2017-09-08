# for base container all possible packages
# should be installed for faster builds
name={{lxc_name}}

[ -z "{{create}}" ] || ./fire lxc-init $name --mount-cache= --mount-ssh --no-login

lxc-stop -n $name || true
config=/var/lib/lxc/$name/config
placeholder='###fireq'
mount_cache=${mount_cache:-"/var/cache/fireq"}

# create required directories
mkdir -p $mount_cache/{pip,npm}
mkdir -p /var/tmp/data /var/spool/ftp

sed -i '/'$placeholder'/Q' $config
cat <<EOF >> $config
$placeholder
lxc.mount.entry = $mount_cache/pip root/.cache/pip/ none bind,create=dir
lxc.mount.entry = $mount_cache/npm root/.npm none bind,create=dir
# apt-get uses lock files, so we can't use shared dpkg cache on CI
#lxc.mount.entry = $mount_cache/dpkg var/cache/apt/archives/ none bind,create=dir

lxc.mount.entry = /var/tmp/data var/tmp/data none bind,create=dir
lxc.mount.entry = /var/spool/ftp var/tmp/ftp none bind,create=dir

# let's keep few cores for data containers and webhook
#lxc.cgroup.cpuset.cpus = 0-8

# 12 cores, so let's use resources of 2 cores if full load
lxc-cgroup.cpu.shares = 2
EOF
unset config placeholder mount_cache
./fire lxc-wait --start $name

cat <<"EOF2" | ./fire lxc-ssh $name
{{>header.sh}}

{{>add-chrome.sh}}
{{>add-dbs.sh}}
{{>testing.sh}}

[ -z "{{create}}" ] || (
{{>build.sh}}

testing=
prepopulate=
{{>deploy.sh}}
)

cat <<EOF > /etc/systemd/system/fix-run-directory.service
[Unit]
Description=Fix issues with /var/run/* directories
Before=local-fs.target

[Service]
Type=oneshot
ExecStart=/bin/systemd-tmpfiles --create

[Install]
RequiredBy=local-fs.target
EOF
systemctl enable fix-run-directory

cat <<EOF > /etc/profile.d/activate.sh
[ -f {{activate}} ] && . {{activate}}
EOF

# cleanup
rm -rf {{repo}}
rm /etc/systemd/system/{{name}}* || true
systemctl disable nginx elasticsearch mongod

# cleanup apt-get
apt-get clean -y
rm /var/lib/apt/lists/lock || true
rm /var/lib/dpkg/lock || true
rm /var/cache/apt/archives/lock || true
# don't need unexpected apt-get running
echo 'APT::Periodic::Enable "0";' > /etc/apt/apt.conf.d/10periodic
EOF2
lxc-stop -n $name
