**Minimal requirements:**
2GB RAM, 4GB Free space

Replace `<ip_or_domain>` with public IP address or domain where superdesk'll be accessible.

## Install on fresh Ubuntu 16.04
```sh
curl -s https://raw.githubusercontent.com/superdesk/fireq/master/files/superdesk/install | sudo bash
# Open http://<ip_or_domain> in browser
# login: admin
# password: admin
```

## Install in LXC container

###[Prepare LXC](../../docs/lxc.md)

```sh
# initilize new container
(echo name=sd; curl -s https://raw.githubusercontent.com/superdesk/fireq/master/files/superdesk/lxc-init) | sudo bash
# install superdesk to container
curl -s https://raw.githubusercontent.com/superdesk/fireq/master/files/superdesk/install | ssh root@sd
# expose port 80 from container to host
iptables -t nat -A PREROUTING -p tcp -i eth0 --dport 80 -j DNAT --to-destination $(sudo lxc-info -iH -n sd)
```

## Stuff after installation
```sh
cat /etc/superdesk.sh # config
ll /opt/superdesk/env # virtualenv
source /opt/superdesk/env/bin/activate # activate virtualenv and loads variables from /etc/superdesk.sh

ll /etc/supervisor/conf.d/ # supervisor configs
supervisorctl status
supervisorctl status client # it's "grunt server"
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
curl -s https://raw.githubusercontent.com/superdesk/fireq/master/files/superdesk/install | sudo bash
# it's safe to run many times
```

## Emails
By default it uses dev SMTP server, which logs all emails to files, you can access them by http://<ip_or_domain>/mail/. If you want real emails, then you should have a proper SMTP server configured and then update settings in `/etc/superdesk.sh`:
```sh
$ cat << EOF >> /etc/superdesk.sh
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

## Sample data
By default install script creates minimal database for Superdesk with one `admin` user. If you want more data on the test instance try this:
```sh
# modify DB_NAME in /etc/superdesk.sh
source /opt/superdesk/env/bin/activate
cd /opt/superdesk/server
./manage.py app:initialize_data --sample-data
# go http://<ip_or_domain> in browser
```
