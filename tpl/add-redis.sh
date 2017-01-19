## redis
if ! _skip_install redis-server; then
    apt-get -y install software-properties-common
    add-apt-repository -y ppa:chris-lea/redis-server
    apt-get -y install --no-install-recommends redis-server

    systemctl enable redis-server
    systemctl restart redis-server
fi
