cat <<"EOF" > /etc/nginx/sites-enabled/{{label}}
{{#hosts}}
server {
    listen  80;
    listen [::]:80;

    server_name {{host}};
    access_log /var/log/nginx/{{name}}.access.log;

    location /.well-known {
        root /var/tmp;
    }
    location / {
        return 302 https://$host$request_uri;
    }
}
server {
    listen  443 ssl http2;
    listen [::]:443 ssl http2;
    server_name {{host}};
    access_log /var/log/nginx/{{name}}.access.log;

    location / {
        proxy_pass "http://{{name}}:80";
        expires epoch;
    }

    location /ws {
        proxy_pass "http://{{name}}:80";
        proxy_buffering off;
        proxy_read_timeout 600;
        proxy_http_version 1.1;
        proxy_set_header Host $http_host;
        proxy_set_header Upgrade $http_upgrade;
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
{{/hosts}}
EOF
# proxy ssh ports
cat <<"EOF" > /etc/nginx/sites-ssh-enabled/{{label}}
{{#proxy_ssh}}
server {
    listen {{port}};
    proxy_pass {{name}}:22;
}
{{/proxy_ssh}}
EOF
{{#proxy_ssh}}
cat <<"EOF2" | {{ssh}} {{name}}
cat <<"EOF" > /etc/nginx/conf.d/ssh.inc
location /ssh {
    add_header Content-Type text/plain;
    return 200 '{{ssh}} root@{{host}} -p {{port}}';
}
EOF
nginx -s reload
EOF2
{{/proxy_ssh}}
nginx -s reload
