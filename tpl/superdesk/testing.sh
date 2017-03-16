{{#db_local}}
mongo_init='path=/tmp/mongodb; [ -d $path ] || mkdir $path; chown mongodb:mongodb $path'
cat <<EOF > /etc/systemd/system/mongo-init.service
[Unit]
Description=Mongo init
Before=local-fs.target

[Service]
Type=oneshot
ExecStart=/bin/sh -c "$mongo_init"

[Install]
RequiredBy=local-fs.target
EOF
systemctl enable mongo-init
systemctl start mongo-init

# tune elasticsearch
cat <<EOF > /etc/elasticsearch/elasticsearch.yml
network.bind_host: 0.0.0.0
node.local: true
discovery.zen.ping.multicast: false
path.repo: /var/tmp/elasticsearch
index.number_of_replicas: 0
index.store.type: memory
#index.refresh_interval: 30s

# Next setting break behave tests
# index.number_of_shards: 1
EOF
echo 'log4j.rootLogger=OFF' > /etc/elasticsearch/logging.yml

# tune mongo
cat <<EOF > /etc/mongod.conf
storage:
  dbPath: /tmp/mongodb
  journal:
    enabled: false
  engine: wiredTiger

net:
  port: 27017
  bindIp: 0.0.0.0
EOF

systemctl restart elasticsearch mongod
wait_elastic
{{/db_local}}

# TODO: update superdesk-core to check elastic instead of directory
# "/tmp/es-backups" because need to fix superdesk/tests/__init__.py#L78
mkdir -p /tmp/es-backups /var/tmp/elasticsearch
