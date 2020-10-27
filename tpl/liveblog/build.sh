### build
{{>superdesk/build-init.sh}}

{{>superdesk/build-src.sh}}

cd {{repo_server}}
[ -f dev-requirements.txt ] && req=dev-requirements.txt || req=requirements.txt
time pip install -U -r $req

cd {{repo}}
time npm i monorepo --no-audit
time npm install --unsafe-perm --no-audit
time npm i gulp grunt grunt-cli --no-audit
time npm run build

