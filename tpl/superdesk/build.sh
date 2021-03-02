### build
{{>build-init.sh}}

{{>build-src.sh}}

cd {{repo_server}}
[ -f dev-requirements.txt ] && req=dev-requirements.txt || req=requirements.txt
time pip install -Ur $req

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
time npm ci --unsafe-perm || time npm install --unsafe-perm --no-audit
