### [Prepare LXC](../../docs/lxc.md)

## Install a {{name}} to LXC container
```sh
# create clean directory
path=~/{{name}}
mkdir $path && cd $path
# it mounts next directories inside the container
# - current directory $(pwd) to /opt/superdesk
# - /var/cache/fireq for pip, npm, dpkg caches and logs
sudo bash -c "name={{scope}} mount_src=$(pwd); $(curl -s https://raw.githubusercontent.com/superdesk/fireq/master/files/superdesk/lxc-init)"
(echo host=$(hostname); curl -s https://raw.githubusercontent.com/superdesk/fireq/master/files/{{name}}-dev/install) | bash

# open http://{{scope}} in browser to access superdesk

# current directory is mounted inside the container,
# some files could be created by root during installation, so
sudo chown -R <your_user> .
ls -l ./client-core # superdesk-client-core
ls -l ./server-core # superdesk-core
ls -l /var/cache/fireq/log/sd/ # logs
```

### Inside the container
```sh
ssh root@{{scope}}
systemctl status superdesk
systemctl restart superdesk
systemctl status superdesk-client

cat {{config}} # config
env | sort # print all env variables
ll /opt/{{name}}/env # virtualenv
source /opt/{{name}}/env/bin/activate # active by default, loads variables from {{config}}

ll /etc/nginx/conf.d/ # nginx configs

# logs
journal -u superdesk* -f
ll /var/log/superdesk
```

## We can create separate LXC container for tests
```sh
sudo bash -c "name={{scope}}tests mount_src=~/{{name}}; $(curl -s https://raw.githubusercontent.com/superdesk/fireq/master/files/superdesk/lxc-init)"
# inside the container
(echo testing=1 host=$(hostname); curl -s https://raw.githubusercontent.com/superdesk/fireq/master/files/{{name}}-dev/install) | bash

# and run tests like this
cd ~/superdesk/client-core
protractor protractor.conf.js --baseUrl http://{{scope}}test --params.baseBackendUrl http://{{scope}}test/api
```
