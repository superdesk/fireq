### [Prepare LXC](../../docs/lxc.md)

## Install a superdesk to LXC container
```sh
# create clean directory
path=~/superdesk
mkdir $path && cd $path
# it mounts next directories inside the container
# - current directory $(pwd) to /opt/superdesk
# - /var/cache/fireq for pip, npm, dpkg caches and logs
sudo bash -c "name=sd mount_src=$(pwd); $(curl -s https://raw.githubusercontent.com/superdesk/fireq/master/files/superdesk/lxc-init)"
(echo host=$(hostname); curl -s https://raw.githubusercontent.com/superdesk/fireq/master/files/superdesk-dev/install) | bash

# open http://sd in browser to access superdesk

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
systemctl status superdesk
systemctl restart superdesk
systemctl status superdesk-client

cat /etc/superdesk.sh # config
env | sort # print all env variables
ll /opt/superdesk/env # virtualenv
source /opt/superdesk/env/bin/activate # active by default, loads variables from /etc/superdesk.sh

ll /etc/nginx/conf.d/ # nginx configs

# logs
journal -u superdesk* -f
ll /var/log/superdesk
```

## We can create separate LXC container for tests
```sh
sudo bash -c "name=sdtests mount_src=~/superdesk; $(curl -s https://raw.githubusercontent.com/superdesk/fireq/master/files/superdesk/lxc-init)"
# inside the container
(echo testing=1 host=$(hostname); curl -s https://raw.githubusercontent.com/superdesk/fireq/master/files/superdesk-dev/install) | bash

# and run tests like this
cd ~/superdesk/client-core
protractor protractor.conf.js --baseUrl http://sdtest --params.baseBackendUrl http://sdtest/api
```
