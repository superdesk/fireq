cat <<EOF
[program:rest]
command=/bin/sh -c '. $env/bin/activate && exec gunicorn -b 0.0.0.0:5000 wsgi'
autostart=true
autorestart=true
stdout_logfile=/dev/null
redirect_stderr=true
directory=$repo/server

[program:wamp]
command=/bin/sh -c '. $env/bin/activate && exec python -u ws.py'
autostart=true
autorestart=true
stdout_logfile=/dev/null
redirect_stderr=true
directory=$repo/server
EOF
