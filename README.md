# Install a Superdesk

## Fresh Ubuntu 16.04
```sh
curl https://raw.githubusercontent.com/naspeh-sf/deploy/master/install.sh | sudo sh
```

## LXC container
```sh
./sd lxc-base -n sd0
./sd i -s root@$(lxc-info -n sd0 -iH) --services --dev

# more options
./sd -h
```
