# Install a Superdesk

## Fresh Ubuntu 16.04
```sh
# Replace <you_ip_or_domain> with domain where Superdesk will be accessible
# for example test.superdesk.org
echo "HOST=<you_ip_or_domain>" > /etc/superdesk.sh

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
