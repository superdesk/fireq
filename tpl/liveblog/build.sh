### build
{{>superdesk/build-init.sh}}

{{>superdesk/build-src.sh}}

git config --global url.'https://'.insteadOf git:// ;
# npm >= 7 lockfiles resolve github dependencies to ssh urls
git config --global --add url.https://github.com/.insteadOf ssh://git@github.com/

# The server's Python comes from the repo's .fireq.json ("python": "python3.8"),
# so branches on different versions build from the same base container. Ubuntu
# ships python3.8 on 18.04 only; newer releases get it from the deadsnakes PPA.
python=$(_get_json_value python python3)
if [ "$python" != python3 ]; then
    if ! apt-cache show $python > /dev/null 2>&1; then
        apt-get -y install --no-install-recommends software-properties-common
        add-apt-repository -y ppa:deadsnakes/ppa
        apt-get update
    fi
    apt-get -y install --no-install-recommends \
        $python $python-venv $python-dev $python-distutils
    rm -rf {{repo_env}}
    $python -m venv {{repo_env}}
    _activate
    pip install -U pip wheel setuptools
fi
unset python

cd {{repo_server}}
time pip install 'pip<=20.2.3'
time pip install 'setuptools<50'
[ -f dev-requirements.txt ] && req=dev-requirements.txt || req=requirements.txt
time pip install -U -r $req

cd {{repo}}
# Themes build with the Node from the base container (gulp 3 breaks on newer
# ones), so a client that needs its own Node is taken out of the monorepo
# build and built separately.
client_lockfile=$(jq -r '.lockfileVersion' {{repo_client}}/package-lock.json)
if [ "$client_lockfile" = 3 ]; then
    jq '.packages -= ["client"]' monorepo.json > monorepo.json.tmp
    mv monorepo.json.tmp monorepo.json
fi
time npm install monorepo --no-audit
time npm install --unsafe-perm --no-audit
time npm install gulp grunt grunt-cli --no-audit
time npm run build

if [ "$client_lockfile" = 3 ]; then
(
    cd {{repo_client}}
    {{>build-node-version.sh}}
    # install scripts are skipped, as in the Liveblog GitHub workflow
    time npm ci --unsafe-perm --ignore-scripts
    time npm run build
)
fi
unset client_lockfile

