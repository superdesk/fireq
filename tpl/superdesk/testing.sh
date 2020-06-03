{{#db_local}}
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

systemctl restart mongod
{{/db_local}}

# TODO: update superdesk-core to check elastic instead of directory
# "/tmp/es-backups" because need to fix superdesk/tests/__init__.py#L78
mkdir -p /tmp/es-backups /var/tmp/elasticsearch
