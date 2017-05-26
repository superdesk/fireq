{{#db_local}}
# tune elasticsearch
cat <<EOF > /etc/elasticsearch/elasticsearch.yml
network.bind_host: 0.0.0.0
node.local: true
discovery.zen.ping.multicast: false
path.repo: /var/tmp/elasticsearch
index.number_of_replicas: 0
#index.store.type: memory
#index.refresh_interval: 30s

# Next setting break behave tests
# index.number_of_shards: 1
EOF
echo 'log4j.rootLogger=OFF' > /etc/elasticsearch/logging.yml

# tune mongo
cat <<EOF > /etc/mongod.conf
storage:
  dbPath: /var/lib/mongodb
  journal:
    enabled: false
  engine: wiredTiger

net:
  port: 27017
  bindIp: 0.0.0.0
EOF

systemctl restart elasticsearch mongod
! type wait_elastic || wait_elastic
{{/db_local}}

# TODO: update superdesk-core to check elastic instead of directory
# "/tmp/es-backups" because need to fix superdesk/tests/__init__.py#L78
mkdir -p /tmp/es-backups /var/tmp/elasticsearch
