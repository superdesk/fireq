{{>superdesk/build-init.sh}}

{{>superdesk/build-src-repo.sh}}

cd {{repo}}/server

time pip install -r requirements.txt

cd {{repo}}/client

{{>superdesk/build-node-version.sh}}

time npm install --no-audit
time npm run build
