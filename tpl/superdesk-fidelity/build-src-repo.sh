{{>superdesk/build-src-repo.sh}}

# for now use just master branch by default
GIT_SSH_COMMAND="ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no" \
git -C /tmp/ clone ssh://git@stash.sourcefabric.org:7999/sdp/superdesk-fidelity.git sd_custom
cp -R /tmp/sd_custom/* /opt/superdesk/
rm -R /tmp/sd_custom/
