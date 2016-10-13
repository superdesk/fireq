# Install a Superdesk

## Fresh Ubuntu 16.04
```sh
curl https://raw.githubusercontent.com/naspeh-sf/deploy/master/install.sh | sudo sh
```

## LXC container
```sh
apt-get install lxc

./sd lxc-base -n sd0
./sd i --lxc-name=sd0 --services --prepopulate

# more options
./sd -h
```
