cat <<EOF
server {
    listen 80 default;

$nginx_locations

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

        sub_filter_types application/json;
        sub_filter_once off;
        sub_filter 'http://localhost' 'http://\$host';
    }

    location / {
        root ${repo_client}/dist;

        sub_filter_once off;
        sub_filter_types application/javascript;
        sub_filter 'http://localhost:9000' 'http://\$host:9000';
        sub_filter 'http://localhost:5000' 'http://\$host';
        sub_filter 'ws://localhost:5100' 'ws://\$host/ws';
    }
}
EOF
