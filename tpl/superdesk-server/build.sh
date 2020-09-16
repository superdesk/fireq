{{>build-init.sh}}

#branch=1.4
{{>superdesk/build-src-cores.sh}}

repo={{repo}}/server-core
rm -rf $repo
{{>superdesk/build-src-repo.sh}}

# we always need all packages from main repo to prevent
# errors like: "ImportError: No module named 'analytics'"
cd {{repo}}/server
time pip install -r requirements.txt

cd {{repo_server}}
time pip install -Ur requirements.txt

{{>superdesk/build-sams.sh}}

cd {{repo_client}}
time npm install
