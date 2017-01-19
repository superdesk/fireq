## node & npm
if ! _skip_install nodejs; then
    curl -sL https://deb.nodesource.com/setup_7.x | sudo -E bash -
    apt-get install -y nodejs
fi

[ -f /usr/bin/node ] || ln -s /usr/bin/nodejs /usr/bin/node
npm --version
node --version
