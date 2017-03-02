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
    elastic_version=${elastic_version:-1.7}
    curl https://packages.elastic.co/GPG-KEY-elasticsearch | apt-key add -
    echo "deb https://packages.elastic.co/elasticsearch/$elastic_version/debian stable main" \
        > /etc/apt/sources.list.d/elastic.list

    apt-get -y update
    apt-get -y install --no-install-recommends \
        openjdk-8-jre-headless \
        elasticsearch

    systemctl enable elasticsearch
    unset elastic_version
fi

# tune elasticsearch
config='/etc/elasticsearch/elasticsearch.yml'
[ -f "${config}.bak" ] || mv $config $config.bak
es_backups=/var/tmp/elasticsearch
if [ ! -d "$es_backups" ]; then
    mkdir $es_backups
    chown elasticsearch:elasticsearch $es_backups
fi
cat <<EOF > $config
network.bind_host: 0.0.0.0
node.local: true
discovery.zen.ping.multicast: false
path.repo: $es_backups
index.number_of_replicas: 0
#index.refresh_interval: 30s
#index.store.type: memory

# Next setting break behave tests
# index.number_of_shards: 1
EOF

{{#db_optimize}}
echo 'log4j.rootLogger=OFF' > /etc/elasticsearch/logging.yml
{{/db_optimize}}

systemctl restart elasticsearch
wait_elastic

curl -XPUT 'http://localhost:9200/_snapshot/backups' \
    -d '{"type": "fs", "settings": {"location": "'$es_backups'"}}'
unset config es_backups
