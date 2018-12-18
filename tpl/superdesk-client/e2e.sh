{{>add-chrome.sh}}
{{>add-dbs.sh}}
{{>testing.sh}}

prepopulate=
grunt_build=

{{>deploy.sh}}

# we don't need celery and content_api for e2e tests
cat <<"EOF" > {{repo}}/server/Procfile
rest: gunicorn -b 0.0.0.0:5000 -w 1 -t 300 wsgi
wamp: python3 -u ws.py
EOF
systemctl restart superdesk

cd {{repo_client}}
time npm i protractor-flake
time webdriver-manager update --gecko false

export SCREENSHOTS_DIR=/var/tmp/data/screenshots/{{uid}}
[ -n $E2E_NUM ] && specs="--specs $(cat /var/tmp/specs-part${E2E_NUM:-1})" || specs=

protractor-flake --max-attempts=2 --\
    protractor.conf.js --stackTrace --verbose --troubleshoot\
    --baseUrl 'http://localhost'\
    --params.baseBackendUrl 'http://localhost/api'\
    $specs
