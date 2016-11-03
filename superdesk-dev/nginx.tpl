cat <<EOF
server {
    listen  80;
    listen [::]:80;

    server_name ${name}.test.superdesk.org;

    access_log /var/log/nginx/${name}.access.log;

    location / {
        proxy_pass "http://${lxc}:80";
    }

    location /ws {
        proxy_pass "http://${lxc}:80";
        proxy_buffering off;
        proxy_read_timeout 600;
        proxy_http_version 1.1;
        proxy_set_header Host \$http_host;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    location /robots.txt {
        root /var/www/html;
        expires max;
    }
}
EOF
