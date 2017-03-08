**Minimal requirements:**
2GB RAM, 4GB Free space

## Install a superdesk on fresh Ubuntu 16.04
```sh
curl -s https://raw.githubusercontent.com/superdesk/fireq/master/files/superdesk/install | sudo bash
```

Open your public IP or domain in browser to access superdesk. Use default user with login:**admin** and password:**admin**.

## Install a superdesk in LXC container

###[Prepare LXC](../../docs/lxc.md)

```sh
# initilize new container
(echo name=sd; curl -s https://raw.githubusercontent.com/superdesk/fireq/master/files/superdesk/lxc-init) | sudo bash
# install superdesk to container
curl -s https://raw.githubusercontent.com/superdesk/fireq/master/files/superdesk/install | ssh root@sd
# expose port 80 from container to host
iptables -t nat -A PREROUTING -p tcp -i eth0 --dport 80 -j DNAT --to-destination $(sudo lxc-info -iH -n sd)
```
