# Why LXC
Because we can pack all stuff in **only one LXC container**, it's container like usual OS, so it can run process as much as needed with default init system, opposite to Docker way with one container for one process.

# Installing LXC on Ubuntu 16.04
```
sudo apt-get install lxc
```

# Installing LXC on Ubuntu 14.04
We need Ubuntu 16.04 inside the LXC containers, so for this we need `lxc` package from `trusty-backports` repository.
```sh
echo "deb http://archive.ubuntu.com/ubuntu trusty-backports main restricted universe multiverse" | sudo tee -a /etc/apt/sources.list
sudo apt-get update
sudo apt-get -t trusty-backports install lxc
```

# To access container by it's name
```sh
# Set "10.0.3.1" as first DNS server
# could be different ways, depends on network manager
echo "nameserver 10.0.3.1" | sudo tee -a /etc/resolvconf/resolv.conf.d/head
sudo resolvconf -u
sudo cat /etc/resolv.conf
```
Add container names to `~/.ssh/config` with next settings:
```sh
cat <<EOF >> ~/.ssh/config
Host sd lb
StrictHostKeyChecking no
UserKnownHostsFile /dev/null
EOF
```
When IP changes after reboot or so, no need to modify `~/.ssh/known_hosts` file.

After installation, we can open `http://sd` in browser or go inside by `ssh root@sd`.

# Some useful commands
```sh
sudo lxc-ls -f # list containers
sudo lxc-destroy -fn sd # stop and remove container
sudo lxc-stop -n sd # stop container
sudo lxc-start -n sd # start container
sudo lxc-info -iH -n sd # IP of container
# go inside
sudo lxc-attach -n sd
ssh root@sd
```
