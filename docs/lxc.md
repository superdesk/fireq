# Why LXC
Because we can pack all stuff in **only one LXC container**, it's container like usual OS, so it can run process as much as needed with default init system, opposite to Docker way with one container for one process.

# Installing LXC on Ubuntu 20.04
```
sudo snap install lxd
```

# Installing LXC on Ubuntu 18.04
<!---We need Ubuntu 16.04 inside the LXC containers, so for this we need `lxc` package from `trusty-backports` repository.
```sh
echo "deb http://archive.ubuntu.com/ubuntu trusty-backports main restricted universe multiverse" | sudo tee -a /etc/apt/sources.list
sudo apt-get update
sudo apt-get -t trusty-backports install lxc
```
--->
```sh
sudo apt-get install lxd
```

# To access container by it's name
```sh
# Set "10.0.3.1" as first DNS server
# could be different ways, depends on network manager
echo "nameserver 10.0.3.1" | sudo tee -a /etc/resolv-manual.conf
sudo rm /etc/resolv.conf && unlink /etc/resolv.conf
sudo ln -s /etc/resolv-manual.conf /etc/resolv.conf 
sudo resolvectl dns
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
sudo lxc ls # list containers
sudo lxc delete -f sd # stop and remove container
sudo lxc stop sd # stop container
sudo lxc start sd # start container
sudo lxc copy sd sd1 # clone container
sudo lxc exec sd -- hostname -I # IP of container
# go inside
sudo lxc shell sd
ssh root@sd
```
