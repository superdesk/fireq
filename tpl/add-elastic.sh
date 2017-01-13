### elasticsearch
wget -qO - https://packages.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
echo "deb http://packages.elastic.co/elasticsearch/1.7/debian stable main" \
    > /etc/apt/sources.list.d/elastic.list

apt-get -y update
apt-get -y install --no-install-recommends \
    openjdk-8-jre-headless \
    elasticsearch

# tune elasticsearch
config='/etc/elasticsearch/elasticsearch.yml'
[ -f "${config}.bak" ] || mv $config $config.bak
cat << EOF > $config
network.bind_host: 0.0.0.0
node.local: true
discovery.zen.ping.multicast: false
EOF

systemctl enable elasticsearch
systemctl restart elasticsearch
