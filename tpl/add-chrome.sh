# chrome instead of chromium.
# chromium 59.0.3071.109 fails at creating session.
if ! _skip_install google-chrome-stable; then
    curl -s https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google.list
    apt-get update
    apt-get install -y --no-install-recommends xvfb google-chrome-stable
fi

export CHROME_BIN=$(which google-chrome-stable) && $CHROME_BIN --version
