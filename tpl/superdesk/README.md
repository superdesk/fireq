**Minimal requirements:**
2GB RAM, 4GB Free space

## Install a {{name}} on fresh Ubuntu 16.04
```sh
curl -s https://raw.githubusercontent.com/superdesk/fireq/master/files/{{name}}/install | sudo bash
```

Open your public IP or domain in browser to access {{name}}. Use default user with login:**admin** and password:**admin**.

## Install a {{name}} in LXC container

###[Prepare LXC](../../docs/lxc.md)

```sh
# initilize new container
(echo name={{scope}}; curl -s https://raw.githubusercontent.com/superdesk/fireq/master/files/{{name}}/lxc-init) | sudo bash
# install {{name}} to container
curl -s https://raw.githubusercontent.com/superdesk/fireq/master/files/{{name}}/install | ssh root@{{scope}}
# expose port 80 from container to host
iptables -t nat -A PREROUTING -p tcp -i eth0 --dport 80 -j DNAT --to-destination $(sudo lxc-info -iH -n {{scope}})
```
