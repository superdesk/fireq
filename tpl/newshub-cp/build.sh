{{>superdesk/build-init.sh}}

{{>superdesk/build-src-repo.sh}}

cd {{repo}}
time pip install -r requirements.txt

# required for minimal setup of newshub-cp-lji.git
cp -r -n env/src/newsroom/* .

time npm install --no-audit
time npm run build

