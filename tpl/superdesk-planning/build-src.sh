# Download the Planning repo first
# So the fireq.json file is available
repo={{repo}}/planning
{{>superdesk/build-src-repo.sh}}

# Use the config `superdesk_branch` if set
# Otherwise default to `planning-mvp`
branch=`_get_config_value superdesk_branch planning-mvp`
{{>superdesk/build-src-cores.sh}}
