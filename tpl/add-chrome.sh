if ! _skip_install google-chrome-stable; then
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
    echo "deb http://dl.google.com/linux/chrome/deb/ stable main" \
        > /etc/apt/sources.list.d/google.list
    apt-get update
    apt-get install -y --no-install-recommends xvfb google-chrome-stable

    # don't need unexpected apt-get running
    rm -f /etc/cron.daily/google-chrome

    google-chrome --version
fi
