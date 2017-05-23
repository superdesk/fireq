# elasticsearch
wait_elastic() {
    elastic=0
    while [ $elastic -eq 0 ]
    do
        curl -s "http://localhost:9200" 2>&1 > /dev/null \
            && elastic=1 \
            || echo "waiting for elastic..."
        sleep 5
    done
}
if ! _skip_install elasticsearch; then
    # for elasticsearch 2.4.x declare next
    # elastic_version=2.x
    version=${elastic_version:-1.7}
    curl -s https://packages.elastic.co/GPG-KEY-elasticsearch | apt-key add -
    echo "deb https://packages.elastic.co/elasticsearch/$version/debian stable main" \
        > /etc/apt/sources.list.d/elastic.list

    apt-get -y update
    apt-get -y install --no-install-recommends \
        openjdk-8-jre-headless \
        elasticsearch
    unset version
fi

# tune elasticsearch
cfg='/etc/elasticsearch/elasticsearch.yml'
[ -f "${cfg}.bak" ] || mv $cfg $cfg.bak
es_backups=/var/tmp/elasticsearch
if [ ! -d "$es_backups" ]; then
    mkdir $es_backups
    chown elasticsearch:elasticsearch $es_backups
fi
cat <<EOF > $cfg
network.bind_host: 0.0.0.0
node.local: true
discovery.zen.ping.multicast: false
path.repo: $es_backups
index.number_of_replicas: 0
EOF

systemctl enable elasticsearch
systemctl restart elasticsearch
wait_elastic

curl -s -XPUT 'http://localhost:9200/_snapshot/backups' \
    -d '{"type": "fs", "settings": {"location": "'$es_backups'"}}'
unset cfg es_backups
