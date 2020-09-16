{{>build-init.sh}}

#branch=1.4
{{>superdesk/build-src-cores.sh}}

repo={{repo}}/client-core
rm -rf $repo
{{>superdesk/build-src-repo.sh}}

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

# use superdesk-core from here
cd {{repo_client}}/test-server
time pip install -Ur requirements.txt

{{>superdesk/build-sams.sh}}

cd {{repo_client}}
time npm install --unsafe-perm
# will be used for e2e tests
time node --max-old-space-size=4096  `which grunt` build --webpack-no-progress
