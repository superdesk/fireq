#!/bin/sh
set -v

DEBIAN_FRONTEND=noninteractive
apt-get -y autoremove --purge ntpdate nginx
apt-get -y update
apt-get -y dist-upgrade
apt-get -y install wget software-properties-common

#elasticsearch
wget -qO - https://packages.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
echo "deb http://packages.elastic.co/elasticsearch/1.7/debian stable main" \
    > /etc/apt/sources.list.d/elastic.list

#mongodb
apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv EA312927
echo "deb http://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/3.2 multiverse" \
    > /etc/apt/sources.list.d/mongodb-org-3.2.list

#redis
add-apt-repository -y ppa:chris-lea/redis-server

#nginx
wget -qO - http://nginx.org/keys/nginx_signing.key | sudo apt-key add -
echo "deb http://nginx.org/packages/ubuntu/ xenial nginx" \
    > /etc/apt/sources.list.d/nginx.list

#install
apt-get -y update
apt-get -y install \
    openjdk-8-jre-headless \
    elasticsearch \
    mongodb-org-server \
    redis-server \
    nginx
apt-get -y clean

systemctl enable elasticsearch mongod redis-server nginx
systemctl restart elasticsearch mongod redis-server nginx
