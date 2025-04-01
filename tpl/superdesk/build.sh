### build
{{>build-init.sh}}

{{>build-src.sh}}

cd {{repo_server}}
time pip install -Ur requirements.txt

# Merge the `.fireq.json` file using the `{{fireq_json}}` variable
# which is set from the scope, for superdesk defaults to:
# /opt/superdesk/env/src/superdesk-core/.fireq.json
_merge_json_from_env_file
_print_json_config

{{>build-sams.sh}}

# if grammalecte is enabled in fireq.json, install grammalecte server
{{>build-grammalecte.sh}}

# if video server is enabled in fireq.json, install it
{{>build-videoserver.sh}}

cd {{repo_client}}

{{>build-node-version.sh}}

time npm ci --unsafe-perm || time npm install --unsafe-perm --no-audit
