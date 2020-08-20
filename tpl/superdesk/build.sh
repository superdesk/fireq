### build
{{>build-init.sh}}

{{>build-src.sh}}

cd {{repo_server}}
[ -f dev-requirements.txt ] && req=dev-requirements.txt || req=requirements.txt
time pip install -Ur $req

{{>build-sams.sh}}

# if grammalecte is enabled in fireq.json, install grammalecte server
{{>build-grammalecte.sh}}

# if video server is enabled in fireq.json, install it
{{>build-videoserver.sh}}

cd {{repo_client}}
time npm install --unsafe-perm
