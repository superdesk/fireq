**Minimal requirements:**
2GB RAM, 4GB Free space

Replace `<ip_or_domain>` with public IP address or domain where {{name}}'ll be accessible.

## Install on fresh Ubuntu 16.04
```sh
curl -s https://raw.githubusercontent.com/superdesk/fireq/master/files/{{name}}/install | sudo bash
# Open http://<ip_or_domain> in browser
# login: admin
# password: admin
```

## Install in LXC container

### [Prepare LXC](../../docs/lxc.md)

```sh
# initilize new container
(echo name={{scope}}; curl -s https://raw.githubusercontent.com/superdesk/fireq/master/files/{{name}}/lxc-init) | sudo bash
# install {{name}} to container
curl -s https://raw.githubusercontent.com/superdesk/fireq/master/files/{{name}}/install | ssh root@{{scope}}
# expose port 80 from container to host
iptables -t nat -A PREROUTING -p tcp -i eth0 --dport 80 -j DNAT --to-destination $(sudo lxc-info -iH -n {{scope}})
```

## Stuff after installation
```sh
cat {{config}} # config
ll /opt/{{name}}/env # virtualenv
source /opt/{{name}}/env/bin/activate # activate virtualenv and loads variables from {{config}}

ll /etc/supervisor/conf.d/ # supervisor configs
supervisorctl status
supervisorctl restart all
supervisorctl restart rest wamp capi

ll /etc/nginx/conf.d/ # nginx configs
ll /var/log/superdesk # logs
```

[Available settings.](https://superdesk.readthedocs.io/en/latest/settings.html#default-settings)

## Update
```sh
cd /opt/superdesk
git pull
curl -s https://raw.githubusercontent.com/superdesk/fireq/master/files/{{name}}/install | sudo bash
# it's safe to run many times
```

## Emails
By default it uses dev SMTP server, which logs all emails to files, you can access them by http://<ip_or_domain>/mail/. If you want real emails, then you should have a proper SMTP server configured and then update settings in `{{config}}`:
```sh
$ cat << EOF >> {{config}}
# Uses for build urls in emails
SUPERDESK_CLIENT_URL=http://<ip_or_domain>

# Defaults
MAIL_FROM=superdesk@localhost
MAIL_PASSWORD=
MAIL_PORT=25
MAIL_SERVER=localhost
MAIL_USERNAME=
MAIL_USE_SSL=False
MAIL_USE_TLS=False
EOF

# restart supervisor
$ supervisorctl restart all
```

{{>README.extra.md}}
