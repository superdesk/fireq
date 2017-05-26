{{>superdesk/build.sh}}

# fix "ImportError: No module named 'analytics'"
cd {{repo}}/server
time pip install -r requirements.txt
