# From: http://cvuorinen.net/2017/05/running-angular-tests-in-headless-chrome/
# > Without a remote debugging port, Google Chrome exits immediately.
chrome_opts='--remote-debugging-port=9222 --no-sandbox'
{{>add-chrome.sh}}

cd {{repo_client}}
time npm test
