### build
{{>build-init.sh}}

{{>build-src.sh}}

cd {{repo_server}}
[ -f dev-requirements.txt ] && req=dev-requirements.txt || req=requirements.txt
time pip install -Ur $req

if [ -d ../server-core ]; then
    pip install -Ue ../server-core
fi

cd {{repo_client}}
time npm install --unsafe-perm

if [ -d ../client-core ]; then
    npm link ../client-core
fi
