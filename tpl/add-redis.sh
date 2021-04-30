# redis
if ! _skip_install redis-server; then
    apt-get -y update
    apt-get -y install --no-install-recommends redis-server
    systemctl enable redis-server
    systemctl restart redis-server
fi
