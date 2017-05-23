### build
locale-gen en_US.UTF-8

apt-get update
apt-get -y install --no-install-recommends \
git python3 python3-dev python3-venv \
build-essential libffi-dev \
libtiff5-dev libjpeg8-dev zlib1g-dev \
libfreetype6-dev liblcms2-dev libwebp-dev \
curl libfontconfig libssl-dev \
libxml2-dev libxslt1-dev


{{>build-init.sh}}


## server part
# init virtualenv
env={{repo_env}}
[ -d $env ] && rm -rf $env
python3 -m venv $env
unset env

_activate
pip install -U pip wheel

cd {{repo_server}}
time pip install -U -r requirements.txt
{{#dev}}
[ ! -f dev-requirements.txt ] || time pip install -r dev-requirements.txt

cat <<EOF > /etc/profile.d/activate.sh
if [ -f {{activate}} ]; then
    . {{activate}}
else
    PATH={{repo_client}}/node_modules/.bin/:$PATH
    . {{repo_env}}/bin/activate
fi
EOF
{{/dev}}


## client part
{{>add-node.sh}}

cd {{repo_client}}
time npm install
{{^is_superdesk}}
# liveblog 3.0.9, 3.1.0 versions need bower
if [ -f bower.json ]; then
    npm i bower
    time bower --allow-root install
fi
{{/is_superdesk}}

# use default urls here
time \
SUPERDESK_URL=http://localhost/api \
SUPERDESK_WS_URL=ws://localhost/ws \
grunt build --webpack-no-progress
