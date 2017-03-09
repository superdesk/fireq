## Sample data
By default install script creates minimal database for Superdesk with one `admin` user. If you want more data on the test instance try this:
```sh
# modify DB_NAME in /etc/superdesk.sh
source /opt/superdesk/env/bin/activate
cd /opt/superdesk/server
./manage.py app:initialize_data --sample-data
# go http://<ip_or_domain> in browser
```
