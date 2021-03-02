{{>build-init.sh}}

# Fetch the superdesk-core repo first
# So that we can load the config values from .fireq.json
# In case we need a different branch from the superdesk/superdesk repo
repo={{repo}}/server-core
rm -rf $repo
{{>superdesk/build-src-repo.sh}}

#branch=1.4
{{>superdesk/build-src-cores.sh}}

# Merge the `.fireq.json` file using the `{{fireq_json}}` variable
# which is set from the scope, for superdesk defaults to:
# /opt/superdesk/server-core/.fireq.json
_merge_json_from_env_file
_print_json_config

# we always need all packages from main repo to prevent
# errors like: "ImportError: No module named 'analytics'"
cd {{repo}}/server
time pip install -r requirements.txt

cd {{repo_server}}
time pip install -Ur requirements.txt

{{>superdesk/build-sams.sh}}

cd {{repo_client}}
time npm ci || time npm install --no-audit
