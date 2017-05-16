# node & npm
if ! _skip_install nodejs; then
    curl -sL https://deb.nodesource.com/setup_7.x | bash -
    apt-get install -y nodejs

    npm install -g grunt-cli
fi

node --version
npm --version
grunt --version
