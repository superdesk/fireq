## Sample data
By default install script creates minimal database for Superdesk with one `admin` user. If you want more data on the test instance try this:
```sh
# modify DB_NAME in /etc/superdesk.sh
source /opt/superdesk/env/bin/activate
cd /opt/superdesk/server

# way #1
./manage.py app:prepopulate

# way #2
./manage.py app:initialize_data --sample-data
./manage.py users:create -u admin -p admin -e 'admin@example.com' --admin

# go http://<ip_or_domain> in browser
```
