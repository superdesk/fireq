wget -qO - http://nginx.org/keys/nginx_signing.key | sudo apt-key add -
echo "deb http://nginx.org/packages/ubuntu/ xenial nginx" \
    > /etc/apt/sources.list.d/nginx.list

apt-get -y update
apt-get -y install nginx

systemctl enable nginx
systemctl restart nginx
