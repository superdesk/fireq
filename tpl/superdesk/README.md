**Minimal requirements:**
2GB RAM, 4GB Free space

## Install a {{name}} on fresh Ubuntu 16.04
```sh
curl https://raw.githubusercontent.com/superdesk/fireq/master/files/{{name}}/install | sudo bash
```

Open your public IP or domain in browser to access {{name}}.

## Install a {{name}} in LXC container

###[Prepare LXC](../../docs/lxc.md)

```sh
# initilize new container
(echo name={{scope}}; curl https://raw.githubusercontent.com/superdesk/fireq/master/files/{{name}}/lxc-init) | sudo bash
# install {{name}} to container
curl https://raw.githubusercontent.com/superdesk/fireq/master/files/{{name}}/install | lxc-attach --clear-env -n {{scope}} -- /bin/bash
# expose port 80 from container to host
iptables -t nat -A PREROUTING -p tcp -i eth0 --dport 80 -j DNAT --to-destination $(lxc-info -iH -n {{scope}})
```
