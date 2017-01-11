cat <<EOF
server {
    listen 80 default;

    include $path/locations;

    location /ws {
        proxy_pass http://localhost:5100;
        proxy_http_version 1.1;
        proxy_buffering off;
        proxy_read_timeout 3600;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "Upgrade";
    }

    location /api {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        expires epoch;

        sub_filter_types application/json;
        sub_filter_once off;
        sub_filter 'http://localhost' 'http${nginx_ssl}://\$host';
    }

    location /.well-known {
        root /var/tmp;
    }

    location / {
        root ${nginx_static};

        sub_filter_once off;
        sub_filter_types application/javascript;
        sub_filter 'http://localhost:5000' 'http${nginx_ssl}://\$host';
        sub_filter 'ws://localhost:5100' 'ws${nginx_ssl}://\$host/ws';
        sub_filter 'iframely:{key:""}' 'iframely:{key:"$IFRAMELY_KEY"}';
    }
}
EOF
