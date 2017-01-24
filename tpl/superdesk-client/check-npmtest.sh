{{>add-chrome.sh}}
cd {{repo_client}}
time xvfb-run -a npm test
