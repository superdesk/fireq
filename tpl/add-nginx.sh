### nginx
if ! _skip_install nginx; then
    wget -qO - http://nginx.org/keys/nginx_signing.key | sudo apt-key add -
    echo "deb http://nginx.org/packages/ubuntu/ xenial nginx" \
        > /etc/apt/sources.list.d/nginx.list

    apt-get -y update
    apt-get -y install nginx

    systemctl enable nginx
    systemctl restart nginx
fi

path=/etc/nginx/conf.d
cat << "EOF" > $path/params.conf
{{>nginx-params.conf}}
EOF

cat << EOF > $path/default.conf
{{>nginx.conf}}
EOF
unset path
nginx -s reload
