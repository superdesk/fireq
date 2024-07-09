# mongo
if ! _skip_install mongodb-org-server; then
    wget -qO - https://www.mongodb.org/static/pgp/server-4.4.asc | apt-key add -
    echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/4.4 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-4.4.list

    apt-get -y update
    apt-get -y install --no-install-recommends \
#        mongodb-org-server \
        mongodb-org-shell \
        mongodb-org-tools
fi

# tune mongo
cfg=/etc/mongod.conf
[ -f "${cfg}.bak" ] || mv $cfg $cfg.bak
cat <<EOF > $cfg
storage:
  dbPath: /var/lib/mongodb
  journal:
    enabled: true
  engine: wiredTiger

systemLog:
  destination: file
  logAppend: true
  path: /var/log/mongodb/mongod.log

net:
  port: 27017
  bindIp: 0.0.0.0
EOF
unset cfg
systemctl enable mongod
systemctl restart mongod

# set compatibility to latest mongo
# added by abbas
sleep 90
mongo admin --eval 'db.runCommand({setFeatureCompatibilityVersion: "3.4"})'
