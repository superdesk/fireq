{{>superdesk/build.sh}}

chunks=/var/tmp/e2e-chunks.py
cat <<"EOF" > $chunks
{{>e2e-chunks.py}}
EOF
python3 $chunks
unset chunks

# fix "ImportError: No module named 'analytics'"
cd {{repo}}/server
time pip install -r requirements.txt

# will be used for e2e tests
cd {{repo_client}}
time grunt build --webpack-no-progress
