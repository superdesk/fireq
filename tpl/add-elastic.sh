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

# make sure there is new elastic if needed
if [ -f {{fireq_json}} ] && [ `jq ".elastic?" {{fireq_json}}` -eq 7 ]; then
    apt-get -y purge elasticsearch
    dpkg-statoverride --remove /var/log/elasticsearch
    dpkg-statoverride --remove /var/lib/elasticsearch

    wget --quiet https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.7.0-amd64.deb
    wget --quiet https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.7.0-amd64.deb.sha512
    shasum -a 512 -c elasticsearch-7.7.0-amd64.deb.sha512 
    sudo dpkg -i elasticsearch-7.7.0-amd64.deb
else
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
fi

systemctl enable elasticsearch
systemctl restart elasticsearch || journalctl -xe
wait_elastic