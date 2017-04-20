## superdesk-content-api external repository
# it's deprecated but needed in some cases
github=https://github.com/superdesk/superdesk-content-api
path=/opt/superdesk-content-api
env=$path/env

if [ ! -d $path ]; then
    mkdir -p $path
    git clone --depth=1 $github.git $path
fi

cat {{config}} | grep -q PUBLICAPI_MONGO_URI || cat <<"EOF" >> {{config}}
PUBLICAPI_MONGO_URI=${MONGO_URI}_pa
PUBLICAPI_URL=${PUBLICAPI_URL:-"http://$HOST/pubapi"}
EOF

envfile={{repo}}/env.sh
activate=$env/bin/activate
[ -d $env ] && rm -rf $env
python3 -m venv $env
echo 'export PATH=./node_modules/.bin/:$PATH' >> $activate
grep "$envfile" $activate || cat <<EOF >> $activate
set -a
[ -f {{config}} ] && . {{config}}
. $envfile
set +a
EOF
set +ux
. $env/bin/activate
set -ux
unset envfile activate

cd $path
pip install -r requirements.txt
python content_api_manage.py app:prepopulate || true

service=superdesk-pubapi
cat <<EOF > /etc/systemd/system/$service.service
[Unit]
Description=Deprecated $github
Wants=network.target
After=network.target

[Service]
ExecStart=/bin/sh -c '. $env/bin/activate && exec gunicorn -b 0.0.0.0:5050 wsgi'
WorkingDirectory=$path
Restart=always

[Install]
WantedBy=multi-user.target
EOF
systemctl enable $service
systemctl restart $service
unset service

cat <<EOF >> /etc/nginx/conf.d/default.inc
location /pubapi {
    proxy_pass http://localhost:5050;
    proxy_set_header Host $HOST;
    expires epoch;
}
EOF
nginx -s reload
unset path env
