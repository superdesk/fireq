### build
{{>superdesk/build-init.sh}}

{{>superdesk/build-src.sh}}

cd {{repo_server}}
[ -f dev-requirements.txt ] && req=dev-requirements.txt || req=requirements.txt
time pip install -U -r $req

cd {{repo}}
time npm i monorepo
time npm install --unsafe-perm
time npm i gulp grunt grunt-cli
time npm run build

