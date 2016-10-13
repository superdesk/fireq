#!/bin/sh
set -xe

name=superdesk
repo_git=https://github.com/superdesk/superdesk.git
root=$(dirname $(dirname $(realpath -s $0)))
. $root/common/index.sh

envfile() {
    . $root/common/envfile.tpl > $envfile

    cat <<EOF >> $envfile
DEFAULT_SOURCE_VALUE_FOR_MANUAL_ARTICLES=
REUTERS_USERNAME=
REUTERS_PASSWORD=
EOF
}

backend() {
    venv $env
    pip install -U -r $repo/server/requirements.txt

    . $root/common/supervisor.tpl > /etc/supervisor/conf.d/${name}.conf
    systemctl enable supervisor
    systemctl start supervisor || supervisorctl update
}

frontend() {
    _npm
    npm install -g grunt-cli

    cd $repo/client
    npm install
    grunt build --server='http://localhost:5000/api' --ws='ws://localhost:5100'
}

prepopulate() {
    . $env/bin/activate
    cd $repo/server
    python manage.py app:initialize_data
    python manage.py users:create -u admin -p admin -e 'admin@example.com' --admin
}

install
