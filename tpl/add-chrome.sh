# seams google-chrome is more stable on CI then chromium
if ! _skip_install google-chrome-stable; then
    # we use chrome in headless mode, so no need for xvfb
    curl -s https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google.list
    apt-get update
    apt-get install -y --no-install-recommends google-chrome-stable
fi
google-chrome --version

chrome_opts=${chrome_opts:-""}
export CHROME_BIN=/tmp/chrome
cat <<EOF > $CHROME_BIN
#!/bin/sh
google-chrome\
    --headless --disable-gpu\
    --window-size=1920x1080\
    $chrome_opts\
    "\$@"
EOF
chmod +x $CHROME_BIN
