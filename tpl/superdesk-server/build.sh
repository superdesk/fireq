{{>build-init.sh}}

#branch=1.4
{{>superdesk/build-src-dev.sh}}

repo={{repo}}/server-core
rm -rf $repo
{{>superdesk/build-src.sh}}

# we always need all packages from main repo to prevent
# errors like: "ImportError: No module named 'analytics'"
cd {{repo}}/server
time pip install -r requirements.txt

cd {{repo_server}}
time pip install -Ur requirements.txt

cd {{repo_client}}
time npm install
