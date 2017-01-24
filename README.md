# Install a Superdesk

## Fresh Ubuntu 16.04
```sh
curl https://raw.githubusercontent.com/naspeh-sf/deploy/master/files/superdesk/install | sudo bash
```

## LXC container
```sh
apt-get install lxc

./fire lxc-init -n sd0
./fire2 run superdesk/install | ./fire lxc-ssh sd0
```

# Install a Liveblog

## Fresh Ubuntu 16.04
```sh
curl https://raw.githubusercontent.com/naspeh-sf/deploy/master/files/liveblog/install | sudo bash
```
