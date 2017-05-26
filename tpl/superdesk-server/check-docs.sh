_activate
cd {{repo_server}}/docs
make html

cat <<EOF0 > /etc/nginx/conf.d/docs.inc
location /docs {
    alias {{repo_server}}/docs/_build/html;
}
EOF0
