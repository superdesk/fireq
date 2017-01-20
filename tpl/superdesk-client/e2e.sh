{{>add-chrome.sh}}
{{>add-dbs.sh}}

HOST=localhost
HOST_SSL=
{{^db_local}}
DB_NAME=$(hostname)
{{/db_local}}
SUPERDESK_TESTING=True
{{>deploy.sh}}

cat <<"EOF" > /etc/supervisor/conf.d/superdesk.conf
[program:rest]
command=/bin/sh -c '. {{repo_env}}/bin/activate && exec gunicorn -b 0.0.0.0:5000 wsgi'
autostart=true
autorestart=true
stdout_logfile=/tmp/rest.log
redirect_stderr=true
directory={{repo}}/server

[program:wamp]
command=/bin/sh -c '. {{repo_env}}/bin/activate && exec python -u ws.py'
autostart=true
autorestart=true
stdout_logfile=/tmp/wamp.log
redirect_stderr=true
directory={{repo}}/server
EOF
supervisorctl update
supervisorctl restart all

cd {{repo_client}}
npm i protractor-flake
webdriver-manager update
specs=$(cat /var/tmp/specs-part${E2E_NUM:-1})
time xvfb-run -a -s "-ac -screen 0 1920x1080x24"\
    protractor-flake --max-attempts=2 --\
    protractor.conf.js --stackTrace --verbose\
    --baseUrl 'http://localhost'\
    --params.baseBackendUrl 'http://localhost/api'\
    --specs=$specs
