# Download the Planning repo first
# So the fireq.json file is available
repo={{repo}}/superdesk-planning
{{>superdesk/build-src-repo.sh}}

# Use the config `superdesk_branch` if set
# Otherwise default to `planning-mvp`
branch=`_get_json_value superdesk_branch planning-mvp`
{{>superdesk/build-src-cores.sh}}
