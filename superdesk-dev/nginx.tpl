cat <<EOF
server {
    listen  80;
    listen [::]:80;

    server_name ${host};
    access_log /var/log/nginx/${name}.access.log;

    location /.well-known {
        root /var/tmp;
    }
    location / {
        return 301 https://$host$request_uri;
    }
}
server {
    listen  443 ssl http2;
    listen [::]:443 ssl http2;
    ssl_certificate /etc/letsencrypt/live/sd-master.test.superdesk.org/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/sd-master.test.superdesk.org/privkey.pem;

    server_name ${host};
    access_log /var/log/nginx/${name}.access.log;

    location / {
        proxy_pass "http://${name}:80";
        expires epoch;
    }

    location /ws {
        proxy_pass "http://${name}:80";
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

    location /.well-known {
        root /var/tmp;
    }
}
EOF
