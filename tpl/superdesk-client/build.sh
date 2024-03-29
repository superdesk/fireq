{{>build-init.sh}}

# Fetch the superdesk-client-core repo first
# So that we can load the config values from .fireq.json
# In case we need a different branch from the superdesk/superdesk repo
repo={{repo}}/client-core
rm -rf $repo
{{>superdesk/build-src-repo.sh}}

#branch=1.4
{{>superdesk/build-src-cores.sh}}

# Merge the `.fireq.json` file using the `{{fireq_json}}` variable
# which is set from the scope, for superdesk defaults to:
# /opt/superdesk/env/src/superdesk-core/.fireq.json
_merge_json_from_env_file
_print_json_config

chunks=/var/tmp/e2e-chunks.py
cat <<"EOF" > $chunks
{{>e2e-chunks.py}}
EOF
python3 $chunks
unset chunks

# we always need all packages from main repo to prevent
# errors like: "ImportError: No module named 'analytics'"
cd {{repo}}/server
time pip install -r requirements.txt

if [ -d {{repo_client}}/test-server ]; then # handles old server location
    # use superdesk-core from here
    cd {{repo_client}}/test-server
    time pip install -Ur requirements.txt
elif [ -d {{repo_client}}/../server ]; then # handles new test server location: /client/e2e/server
    # use superdesk-core from here
    cd {{repo_client}}/../server
    time pip install -Ur requirements.txt
fi

{{>superdesk/build-sams.sh}}

cd {{repo_client}}
time npm ci --unsafe-perm || time npm install --unsafe-perm --no-audit
time npm run build

