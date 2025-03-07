# mongo
if ! _skip_install mongodb-org-server; then
    wget -qO - https://www.mongodb.org/static/pgp/server-4.4.asc | apt-key add -
    echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/4.4 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-4.4.list

    apt-get -y update
    apt-get -y install --no-install-recommends \
        mongodb-org-shell \
        mongodb-org-tools
fi

