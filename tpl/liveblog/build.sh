### build
{{>superdesk/build-init.sh}}

{{>superdesk/build-src.sh}}

git config --global url.'https://'.insteadOf git:// ;

cd {{repo_server}}
time pip install 'pip<=20.2.3'
time pip install 'setuptools<50'
[ -f dev-requirements.txt ] && req=dev-requirements.txt || req=requirements.txt
time pip install -U -r $req

cd {{repo_client}}
{{>superdesk/build-node-version.sh}}
time npm ci --unsafe-perm || time npm install --unsafe-perm --no-auditinstall
time npm run build

