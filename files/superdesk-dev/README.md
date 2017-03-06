###[Prepare LXC](../../docs/lxc.md)

## Install a superdesk in LXC container
```sh
lxc=sd path=~/superdesk
mkdir $path && cd $path
# by default it mounts next directories inside the container
# - current directory to /opt/superdesk
# - /var/cache/fireq for pip, npm, dpkg caches and logs
(echo name=$lxc; curl https://raw.githubusercontent.com/superdesk/fireq/master/files/superdesk-dev/lxc-init) | sudo bash
(echo host=$lxc; curl https://raw.githubusercontent.com/superdesk/fireq/master/files/superdesk-dev/install) | ssh root@$lxc

# open http://$lxc in browser to access superdesk

# current directory is mounted inside the container,
# some files could be created by root during installation, so
sudo chown -R <your_user> .
ls -l ./client-core # superdesk-client-core
ls -l ./server-core # superdesk-core
ls -l /var/cache/fireq/log/sd/ # logs
```

### Inside the container
```sh
ssh root@sd
ll /etc/supervisor/conf.d/ # supervisor configs
supervisorctl status
supervisorctl status client # it's "grunt server"
supervisorctl restart all
supervisorctl restart rest wamp capi

cat /etc/superdesk.sh # config
env | sort # print all env variables
ll /opt/superdesk/env # virtualenv
source /opt/superdesk/bin/activate # active by default, loads env variables

ll /etc/nginx/conf.d/ # nginx configs
ll /var/log/superdesk # logs
```

## We can create separate LXC container for tests
```sh
lxc=sdtest
(echo name=$lxc; curl https://raw.githubusercontent.com/superdesk/fireq/master/files/superdesk-dev/lxc-init) | sudo bash
(echo host=$lxc testing=1; curl https://raw.githubusercontent.com/superdesk/fireq/master/files/superdesk-dev/install) | ssh root@$lxc

# and run tests like this
cd ~/superdesk/client-core
protractor protractor.conf.js --baseUrl http://sdtest --params.baseBackendUrl http://sdtest/api
```

## Using just for services
```sh
ssh root@sd
systemctl disable supervisor nginx
systemctl stop supervisor nginx

# and use "sd" as host for mongo, elasticsearch, redis
```
