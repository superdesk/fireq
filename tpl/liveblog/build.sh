### build
{{>superdesk/build-init.sh}}

{{>superdesk/build-src.sh}}

git config --global url.'https://'.insteadOf git:// ;

cd {{repo_server}}
time pip install 'pip<=20.2.3'
time pip install 'setuptools<50'
[ -f dev-requirements.txt ] && req=dev-requirements.txt || req=requirements.txt
time pip install -U -r $req

cd {{repo}}
time npm install monorepo --no-audit
time npm install --unsafe-perm --no-audit
time npm install gulp grunt grunt-cli --no-audit
time npm run build

