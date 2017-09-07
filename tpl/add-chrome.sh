# chromium instead of chrome :)
if ! _skip_install chromium-browser; then
    # without gconf-service, chromium fails at creating session %)
    apt-get install -y --no-install-recommends chromium-browser gconf-service
fi
chromium-browser --version

chrome_opts=${chrome_opts:-""}
export CHROME_BIN=/tmp/chrome
cat <<EOF > $CHROME_BIN
#!/bin/sh
/usr/bin/chromium-browser\
    --headless --disable-gpu\
    --window-size=1920x1080\
    $chrome_opts\
    "\$@"
EOF
chmod +x $CHROME_BIN
