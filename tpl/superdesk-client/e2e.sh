{{>add-chrome.sh}}
{{>add-dbs.sh}}
{{>testing.sh}}

host=localhost
host_ssl=
testing=1
prepopulate=

# we don't need celery for e2e tests
cat <<"EOF" > {{repo}}/server/Procfile
rest: gunicorn -c gunicorn_config.py wsgi
wamp: python3 -u ws.py
EOF

{{>deploy.sh}}

cd {{repo_client}}
time npm i protractor-flake
time webdriver-manager update
[ -n $E2E_NUM ] && specs="--specs $(cat /var/tmp/specs-part${E2E_NUM:-1})" || specs=
time xvfb-run -a -s "-ac -screen 0 1920x1080x24"\
    protractor-flake --max-attempts=2 --\
    protractor.conf.js --stackTrace --verbose --troubleshoot\
    --baseUrl 'http://localhost'\
    --params.baseBackendUrl 'http://localhost/api'\
    $specs
