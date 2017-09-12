# redis
if ! _skip_install redis-server; then
    apt-get -y install software-properties-common
    add-apt-repository -y ppa:chris-lea/redis-server
    apt-get -y update
    apt-get -y install --no-install-recommends redis-server || (
        # seems for some systems we must disable PrivateDevices,
        # otherwise redis fails on starting
        # https://bugs.launchpad.net/ubuntu/+source/redis/+bug/1663911
        path=/etc/systemd/system/redis-server.service.d
        mkdir $path
        echo '[Service]' > $path/redis.override.conf
        echo 'PrivateDevices=no' >> $path/redis.override.conf
    )

    systemctl enable redis-server
    systemctl restart redis-server
fi
