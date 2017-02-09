# elasticsearch
wait_elastic() {
    elastic=0
    while [ $elastic -eq 0 ]
    do
        curl -s "http://localhost:9200" 2>&1 > /dev/null \
            && elastic=1 \
            || echo "waiting for elastic..."
        sleep 1
    done
}
if ! _skip_install elasticsearch; then
    curl https://packages.elastic.co/GPG-KEY-elasticsearch | apt-key add -
    echo "deb http://packages.elastic.co/elasticsearch/1.7/debian stable main" \
        > /etc/apt/sources.list.d/elastic.list

    apt-get -y update
    apt-get -y install --no-install-recommends \
        openjdk-8-jre-headless \
        elasticsearch

    systemctl enable elasticsearch
fi

# tune elasticsearch
config='/etc/elasticsearch/elasticsearch.yml'
[ -f "${config}.bak" ] || mv $config $config.bak
{{^db_optimize}}
cat <<EOF > $config
network.bind_host: 0.0.0.0
node.local: true
discovery.zen.ping.multicast: false
index.number_of_replicas: 0
EOF
systemctl restart elasticsearch
wait_elastic
{{/db_optimize}}
{{#db_optimize}}
es_backups=/tmp/es-backups
if [ ! -d "$es_backups" ]; then
    mkdir $es_backups
    chown elasticsearch:elasticsearch $es_backups
fi
echo 'log4j.rootLogger=OFF' > /etc/elasticsearch/logging.yml
cat <<EOF > $config
network.bind_host: 0.0.0.0
node.local: true
discovery.zen.ping.multicast: false
path.repo: $es_backups

index.refresh_interval: 30s
index.store.type: memory

# Next setting break behave tests
# index.number_of_shards: 1
EOF

systemctl restart elasticsearch
wait_elastic
curl -XPUT 'http://localhost:9200/_snapshot/backups' \
    -d '{"type": "fs", "settings": {"location": "'$es_backups'"}}'
unset es_backups
{{/db_optimize}}
unset config
