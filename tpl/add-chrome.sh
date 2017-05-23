# chromium instead of chrome :)
if ! _skip_install chromium-browser; then
    apt-get install -y --no-install-recommends xvfb chromium-browser
fi

# inspired by http://stackoverflow.com/questions/12258086
sed -i -e 's/CHROMIUM_FLAGS/CHROMIUM_FLAGS="--no-sandbox"/' /etc/chromium-browser/default
export CHROME_BIN=$(which chromium-browser) && $CHROME_BIN --version
