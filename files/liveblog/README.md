**Minimal requirements:**
2GB RAM, 4GB Free space

Replace `<ip_or_domain>` with public IP address or domain where liveblog'll be accessible.

## Install on fresh Ubuntu 16.04
```sh
curl -s https://raw.githubusercontent.com/superdesk/fireq/master/files/liveblog/install | sudo bash
# Open http://<ip_or_domain> in browser
# login: admin
# password: admin
```

## Install to LXC container

### [Prepare LXC](../../docs/lxc.md)

```sh
# initilize new container
sudo bash -c "name=lb; $(curl -s https://raw.githubusercontent.com/superdesk/fireq/master/files/liveblog/lxc-init)"
# inside the container install liveblog
curl -s https://raw.githubusercontent.com/superdesk/fireq/master/files/liveblog/install | bash
# expose port 80 from container to host
iptables -t nat -A PREROUTING -p tcp -i eth0 --dport 80 -j DNAT --to-destination $(sudo lxc-info -iH -n lb)
```

## Stuff after installation
```sh
cat /etc/liveblog.sh # config
ll /opt/liveblog/env # virtualenv
source /opt/liveblog/env/bin/activate # activate virtualenv and loads variables from /etc/liveblog.sh

systemctl status liveblog
systemctl restart liveblog

ll /etc/nginx/conf.d/ # nginx configs

# logs
journal -u liveblog -f
ll /var/log/liveblog
```

[Available settings.](https://superdesk.readthedocs.io/en/latest/settings.html#default-settings)

## Update
```sh
cd /opt/liveblog
git pull
source env/bin/activate

cd /opt/liveblog/server
pip install -U -r requirements.txt
./manage.py data:upgrade
./manage.py app:initialize_data

cd /opt/liveblog/client
npm i
grunt build

systemctl restart liveblog
```

## Emails
By default it uses dev SMTP server, which logs all emails to files, you can access them by http://<ip_or_domain>/mail/. If you want real emails, then you should have a proper SMTP server configured and then update settings in `/etc/liveblog.sh`:
```sh
$ cat << EOF >> /etc/liveblog.sh
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

# restart liveblog
$ systemctl restart liveblog

# Also stop dev SMTP server if needed, it uses port 25 on localhost
systemctl stop liveblog-smtp
systemctl disable liveblog-smtp

```

