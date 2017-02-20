{{>init/sd.sh}}

cat <<"EOF" > /etc/nginx/conf.d/tansa.inc
location /tansaclient {
    proxy_pass https://tansa.ntb.no;
    proxy_set_header Host tansa.ntb.no;
}
EOF
