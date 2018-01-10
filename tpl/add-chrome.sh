# seams google-chrome is more stable on CI then chromium
# we use chrome in headless mode, so no need for xvfb

if [ ! -r /etc/apt/sources.list.d/google.list ]; then
    curl -s https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google.list
fi

apt-get update
apt-get install -y --no-install-recommends google-chrome-stable
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
