### node & npm
add() {
    _skip_install nodejs && return 0
    curl -sL https://deb.nodesource.com/setup_7.x | sudo -E bash -
    apt-get install -y nodejs
}
add

[ -f /usr/bin/node ] || ln -s /usr/bin/nodejs /usr/bin/node
npm --version
node --version
