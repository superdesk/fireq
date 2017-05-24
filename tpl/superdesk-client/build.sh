{{>superdesk/build.sh}}

_activate

# fix for "ImportError: No module named 'analytics'"
pip install -e git+git://github.com/superdesk/superdesk-analytics.git#egg=superdesk-analytics

# will be used for e2e tests
time grunt build --webpack-no-progress
