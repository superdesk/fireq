{{>init/sd.sh}}


cat <<"EOF" >> {{config}}
{{>init/.amazon.sh}}
AMAZON_CONTAINER_NAME='sd-frankfurt-test'
AMAZON_REGION=eu-central-1
EOF

cat <<"EOF" > /etc/nginx/conf.d/media.inc
# serve directly from amazon
location /api/upload-raw/ {
    rewrite ^/api/upload-raw/(.*)$ https://sd-frankfurt-test.s3-eu-central-1.amazonaws.com/fil-master/$1;
}
EOF
