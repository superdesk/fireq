{{>superdesk/build-init.sh}}

{{>superdesk/build-src-repo.sh}}

cd {{repo}}
time pip install -r requirements.txt

time npm install
time npm run build
