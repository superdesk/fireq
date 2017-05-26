### build
{{>build-init.sh}}

{{^develop}}
{{>build-src.sh}}
{{/develop}}
{{#develop}}
{{>build-src-dev.sh}}
[ ! -d {{repo}}/client-core ] || (
    cd {{repo}}/client-core
    time npm link
)
{{/develop}}

cd {{repo_server}}
[ -f dev-requirements.txt ] && req=dev-requirements.txt || req=requirements.txt
time pip install -U -r $req

cd {{repo_client}}
time npm install
