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

## Install to LXC container

### [Prepare LXC](../../docs/lxc.md)

```sh
# initilize new container
sudo bash -c "name=sd; $(curl -s https://raw.githubusercontent.com/superdesk/fireq/master/files/superdesk/lxc-init)"
# inside the container install superdesk
curl -s https://raw.githubusercontent.com/superdesk/fireq/master/files/superdesk/install | bash
# expose port 80 from container to host
iptables -t nat -A PREROUTING -p tcp -i eth0 --dport 80 -j DNAT --to-destination $(sudo lxc-info -iH -n sd)
```

## Stuff after installation
```sh
cat /etc/superdesk.sh # config
ll /opt/superdesk/env # virtualenv
source /opt/superdesk/env/bin/activate # activate virtualenv and loads variables from /etc/superdesk.sh

systemctl status superdesk
systemctl restart superdesk

ll /etc/nginx/conf.d/ # nginx configs

# logs
journal -u superdesk -f
ll /var/log/superdesk
```

[Available settings.](https://superdesk.readthedocs.io/en/latest/settings.html#default-settings)

## Update
```sh
cd /opt/superdesk
git pull
source env/bin/activate

cd /opt/superdesk/server
pip install -U -r requirements.txt
./manage.py data:upgrade
./manage.py app:initialize_data

cd /opt/superdesk/client
npm i
grunt build

systemctl restart superdesk
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

# restart superdesk
$ systemctl restart superdesk

# Also stop dev SMTP server if needed, it uses port 25 on localhost
systemctl stop superdesk-smtp
systemctl disable superdesk-smtp

```

## Sample data
By default install script creates minimal database for Superdesk with one `admin` user. If you want more data on the test instance try this:
```sh
# modify DB_NAME in /etc/superdesk.sh
source /opt/superdesk/env/bin/activate
cd /opt/superdesk/server

# way #1
./manage.py app:prepopulate

# way #2
./manage.py app:initialize_data --sample-data
./manage.py users:create -u admin -p admin -e 'admin@example.com' --admin

# go http://<ip_or_domain> in browser
```
