if [ -f {{fireq_json}} ] && [ `jq ".grammalecte?" {{fireq_json}}` == "true" ]; then
    apt-get -y update
    apt-get install -y --no-install-recommends locales unzip

    sed -i "s/# en_US.UTF-8/en_US.UTF-8/" /etc/locale.gen
    locale-gen

    mkdir /opt/grammalecte
    cd /opt/grammalecte
    wget https://superdesk-test.s3-eu-west-1.amazonaws.com/sd-sdsite/Grammalecte-fr-v1.2.zip
    unzip Grammalecte-fr-v1.2.zip
    rm -f Grammalecte-fr-v1.2.zip
fi
