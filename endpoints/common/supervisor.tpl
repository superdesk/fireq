cat <<EOF
[program:rest]
command=/bin/sh -c '. $env/bin/activate && exec gunicorn -b 0.0.0.0:5000 wsgi'
autostart=true
autorestart=true
stdout_logfile=/var/log/$name/rest.log
redirect_stderr=true
directory=$repo/server

[program:wamp]
command=/bin/sh -c '. $env/bin/activate && exec python -u ws.py'
autostart=true
autorestart=true
stdout_logfile=/var/log/$name/wamp.log
redirect_stderr=true
directory=$repo/server

[program:work]
command=/bin/sh -c '. $env/bin/activate && exec celery -A worker worker --loglevel=DEBUG'
user=nobody
autostart=true
autorestart=true
startsecs=10
killasgroup=true
stdout_logfile=/var/log/$name/work.log
redirect_stderr=true
directory=$repo/server


[program:beat]
command=/bin/sh -c '. $env/bin/activate && exec celery -A worker beat --loglevel=DEBUG --pid='
user=nobody
autostart=true
autorestart=true
startsecs=10
stdout_logfile=/var/log/$name/beat.log
redirect_stderr=true
directory=$repo/server

$supervisor_append
EOF
