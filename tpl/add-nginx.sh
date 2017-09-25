# nginx
if ! _skip_install nginx; then
    curl -s http://nginx.org/keys/nginx_signing.key | apt-key add -
    echo "deb http://nginx.org/packages/ubuntu/ xenial nginx" \
        > /etc/apt/sources.list.d/nginx.list

    apt-get -y update
    apt-get -y install nginx
fi

path=/etc/nginx/conf.d
cat <<EOF > $path/default.conf
server {
    listen 80 default;

    include $path/*.inc;
}
EOF
cat <<EOF > $path/default.inc
{{>nginx.conf}}
EOF
cat <<"EOF" > $path/params.conf
{{>nginx-params.conf}}
EOF
unset path
systemctl enable nginx
systemctl restart nginx
