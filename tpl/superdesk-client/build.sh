{{>superdesk/build.sh}}

# fix for "ImportError: No module named 'analytics'"
pip install -e git+git://github.com/superdesk/superdesk-analytics.git#egg=superdesk-analytics
