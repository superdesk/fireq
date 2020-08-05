### build
{{>build-init.sh}}

{{>build-src.sh}}

cd {{repo_server}}
[ -f dev-requirements.txt ] && req=dev-requirements.txt || req=requirements.txt
time pip install -Ur $req

{{>build-sams.sh}}

cd {{repo_client}}
time npm install --unsafe-perm
