{{>superdesk/build.sh}}

cd {{repo}}/server
# here are some deployment dependencies: gunicorn, etc.
time pip install -r requirements.txt
