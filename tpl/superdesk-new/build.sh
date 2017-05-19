locale-gen en_US.UTF-8

apt-get update
apt-get -y install --no-install-recommends \
git python3 python3-dev python3-venv \
build-essential libffi-dev \
libtiff5-dev libjpeg8-dev zlib1g-dev \
libfreetype6-dev liblcms2-dev libwebp-dev \
curl libfontconfig libssl-dev \
libxml2-dev libxslt1-dev

repo={{repo}}
github=https://github.com/superdesk
[ -d $repo ] && cd $repo || (
mkdir $repo
cd $repo
git clone $github/superdesk-core.git server-core
git clone $github/superdesk-client-core.git client-core
)
unset repo github


## client part
{{>add-node.sh}}
cd {{repo}}/client-core
time npm link

# use default urls here
time \
SUPERDESK_URL=http://localhost/api \
SUPERDESK_WS_URL=ws://localhost/ws \
grunt build --webpack-no-progress


## server part
env={{repo_env}}
[ -d $env ] && rm -rf $env
python3 -m venv $env

_activate
pip install -U pip wheel

cd {{repo}}/server-core
time pip install -e .
time pip install -r requirements.txt
