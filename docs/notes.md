### DigitalOcean

```sh
# Droplet: 2 GB Memory / 40 GB Disk / FRA1 - Ubuntu 16.04.1 x64
# IP: 139.59.154.138

$ ssh root@139.59.154.138
$ (echo HOST=139.59.154.138; curl https://raw.githubusercontent.com/naspeh-sf/deploy/master/files/superdesk/install) | sudo bash

$ cat /etc/superdesk.sh
HOST=139.59.154.138
HOST_SSL=''
DB_HOST='localhost'
DB_NAME='superdesk'
SUPERDESK_TESTING=''

MONGO_URI=mongodb://${DB_HOST}/${DB_NAME}
LEGAL_ARCHIVE_URI=${MONGO_URI}_la
ARCHIVED_URI=${MONGO_URI}_ar
CONTENTAPI_MONGO_URI=${MONGO_URI}_ca

ELASTICSEARCH_URL=http://${DB_HOST}:9200
ELASTICSEARCH_INDEX=${DB_NAME}
CONTENTAPI_ELASTICSEARCH_INDEX=${ELASTICSEARCH_INDEX}_ca

# go to http://139.59.154.138
# login: admin
# password: admin
# then go http://139.59.154.138/#/profile/ to change admin password and info
```

Change accordingly SMTP settings:
```sh
$ cat << EOF >> /etc/superdesk.sh
# Defaults
MAIL_FROM=superdesk@localhost
MAIL_PASSWORD=
MAIL_PORT=25
MAIL_SERVER=localhost
MAIL_USERNAME=
MAIL_USE_SSL=False
MAIL_USE_TLS=False
EOF

# resatart supervisor
$ supervisorctl restart all
```

If you need to change `HOST`
```sh
# change it in /etc/superdesk.sh
$ curl https://raw.githubusercontent.com/naspeh-sf/deploy/master/files/superdesk/deploy | sudo bash
```
