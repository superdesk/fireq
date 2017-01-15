### elasticsearch
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
add() {
    _skip_install elasticsearch && return 0
    wget -qO - https://packages.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
    echo "deb http://packages.elastic.co/elasticsearch/1.7/debian stable main" \
        > /etc/apt/sources.list.d/elastic.list

    apt-get -y update
    apt-get -y install --no-install-recommends \
        openjdk-8-jre-headless \
        elasticsearch

    systemctl enable elasticsearch
}
add

# tune elasticsearch
config='/etc/elasticsearch/elasticsearch.yml'
[ -f "${config}.bak" ] || mv $config $config.bak
cat << EOF > $config
network.bind_host: 0.0.0.0
node.local: true
discovery.zen.ping.multicast: false
EOF
systemctl restart elasticsearch
wait_elastic
